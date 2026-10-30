import os

import pytest

PAGE_URL = "file://" + os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "templates", "bill.html")


@pytest.fixture(scope="session")
def browser(tmp_path_factory):
    """A headless Chrome shared by the page tests; they are skipped when it can't be started."""
    selenium = pytest.importorskip("selenium")
    from selenium import webdriver

    options = webdriver.ChromeOptions()
    for argument in ("--headless=new", "--no-sandbox", "--disable-dev-shm-usage", "--window-size=1300,1000"):
        options.add_argument(argument)
    # Saved files from the page go to a temporary folder instead of the user's downloads.
    options.add_experimental_option("prefs", {"download.default_directory": str(tmp_path_factory.mktemp("downloads"))})
    try:
        driver = webdriver.Chrome(options=options)
    except Exception as error:  # no Chrome or chromedriver on this machine
        pytest.skip(f"Chrome is not available: {error}")
    yield driver
    driver.quit()


@pytest.fixture
def page(browser):
    """The sheet opened fresh, in Korean."""
    browser.get(PAGE_URL)
    browser.execute_script("try { localStorage.clear(); } catch (e) {}")
    browser.get(PAGE_URL)
    return browser
