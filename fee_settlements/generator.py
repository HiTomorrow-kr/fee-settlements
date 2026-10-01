import base64
import json
import os
from datetime import datetime

from . import config

PAGE_PATH = os.path.join(config.TEMPLATES_DIR, "bill.html")


class GenerateError(Exception):
    """The sheet could not be turned into a PDF; the message says why."""


def default_output_path() -> str:
    return os.path.join(config.IMAGES_DIR, f"settlement_{datetime.now():%Y%m%d_%H%M%S}.pdf")


def check_state(text: str) -> None:
    """Raises GenerateError unless the text is a sheet saved by the page (its "Save JSON" button)."""
    try:
        state = json.loads(text)
    except json.JSONDecodeError as e:
        raise GenerateError(f"not a saved sheet: {e}") from e
    if not (isinstance(state, dict) and state.get("version") == 1 and isinstance(state.get("fields"), dict)):
        raise GenerateError("not a saved sheet")


def generate_pdf(state_text: str, language: str | None, output_path: str) -> str:
    """Fills the sheet page with a saved sheet and prints it to an A4 landscape PDF.

    Args:
        state_text (str): The JSON saved by the page.
        language (str | None): "ko" or "en"; None keeps the language saved in the sheet.
        output_path (str): Where the PDF is written.

    Returns:
        str: output_path.
    """
    check_state(state_text)
    from selenium import webdriver  # imported here so the other commands work without selenium

    options = webdriver.ChromeOptions()
    for argument in ("--headless=new", "--no-sandbox", "--disable-dev-shm-usage", "--window-size=1300,1000"):
        options.add_argument(argument)
    try:
        driver = webdriver.Chrome(options=options)
    except Exception as e:  # no Chrome or chromedriver on this host
        raise GenerateError(f"Chrome is not available: {e}") from e
    try:
        driver.get("file://" + PAGE_PATH)
        state = driver.execute_script("return parseState(arguments[0])", state_text)
        if state is None:
            raise GenerateError("not a saved sheet")
        driver.execute_script("writeState(arguments[0]); if (arguments[1]) applyLang(arguments[1]);", state, language)
        pdf = driver.execute_cdp_cmd("Page.printToPDF", {"preferCSSPageSize": True, "printBackground": True})
    finally:
        driver.quit()
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(base64.b64decode(pdf["data"]))
    return output_path
