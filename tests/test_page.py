import base64
import json
import re
import time

from conftest import PAGE_URL
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


def field(page, name, copy="office"):
    return page.find_element(By.CSS_SELECTOR, f'[data-copy="{copy}"] [data-field="{name}"]')


def fee_cell(page, row, column, copy="office"):
    """A cell of the item table: row and column are 1-based, the amount of the last group is column 8."""
    return page.find_element(By.CSS_SELECTOR, f'[data-copy="{copy}"] [data-field="fees"] tr:nth-child({row}) td:nth-child({column})')


def meter(page, name, month, column, copy="office"):
    return page.find_element(By.CSS_SELECTOR, f'[data-copy="{copy}"] [data-meter="{name}"][data-m="{month}"][data-col="{column}"]')


def type_over(element, text):
    element.click()
    element.send_keys(Keys.CONTROL, "a")
    element.send_keys(text)


def clear(element):
    element.click()
    element.send_keys(Keys.CONTROL, "a")
    element.send_keys(Keys.DELETE)


def text_of(page, selector):
    return page.execute_script("return document.querySelector(arguments[0]).textContent", selector)


def test_left_copy_is_mirrored_to_the_right_copy(page):
    field(page, "address").send_keys("Room 547")
    fee_cell(page, 1, 2).send_keys("46,290")
    assert field(page, "address", "resident").text == "Room 547"
    assert fee_cell(page, 1, 2, "resident").text == "46,290"


def test_right_copy_cannot_be_edited(page):
    assert page.execute_script('return document.querySelectorAll(\'[data-copy="resident"] [contenteditable]\').length') == 0
    assert page.execute_script('return document.querySelectorAll(\'[data-copy="office"] [contenteditable]\').length') > 0


def test_vat_and_monthly_total_follow_the_tax_cells(page):
    type_over(fee_cell(page, 11, 8), "168,560")
    assert fee_cell(page, 12, 8).text == "16,860"
    type_over(fee_cell(page, 13, 8), "31,130")
    assert field(page, "month-total").text == "216,550"
    assert field(page, "month-total", "resident").text == "216,550"


def test_vat_is_rounded_to_the_nearest_ten_won(page):
    for taxable, vat in (("12,345", "1,230"), ("12,350", "1,240")):
        type_over(fee_cell(page, 11, 8), taxable)
        assert fee_cell(page, 12, 8).text == vat


def test_vat_can_be_typed_over_and_the_total_follows(page):
    type_over(fee_cell(page, 11, 8), "100,000")
    type_over(fee_cell(page, 12, 8), "1,000")
    assert field(page, "month-total").text == "101,000"


def test_settlement_amount_follows_the_settlement_total_with_the_won_sign(page):
    type_over(field(page, "settle-total"), "216,050")
    assert field(page, "settlement").text == "216,050원"
    assert field(page, "settlement", "resident").text == "216,050원"


def test_meter_cells_take_digits_and_one_decimal_point(page):
    cell = meter(page, "수도", 1, "curr")
    cell.send_keys("19a,3.9가6x")
    assert cell.text == "193.96"


def test_meter_readings_get_thousands_separators(page):
    cell = meter(page, "전기", 1, "curr")
    cell.send_keys("1234567")
    assert cell.text == "1,234,567"


def test_current_reading_carries_into_the_next_months_previous_reading(page):
    meter(page, "전기", 1, "curr").send_keys("19329")
    assert meter(page, "전기", 2, "prev").text == "19,329"
    assert meter(page, "전기", 2, "prev", "resident").text == "19,329"
    assert meter(page, "수도", 2, "prev").text == ""  # other meters are not touched


def test_switching_the_language_changes_the_labels_of_both_copies(page):
    assert text_of(page, '[data-copy="office"] h1') == "중간관리비 (관리소용)"
    page.find_element(By.CSS_SELECTOR, '[data-lang="en"]').click()
    assert text_of(page, '[data-copy="office"] h1') == "Interim Maintenance Fee (Office Copy)"
    assert text_of(page, '[data-copy="resident"] h1') == "Interim Maintenance Fee (Moving-out Resident Copy)"
    assert page.execute_script("return document.documentElement.lang") == "en"
    page.find_element(By.CSS_SELECTOR, '[data-lang="ko"]').click()
    assert text_of(page, '[data-copy="resident"] h1') == "중간관리비 (전출자용)"


def test_an_item_name_typed_over_survives_a_language_switch(page):
    type_over(fee_cell(page, 2, 1), "Custom")
    page.find_element(By.CSS_SELECTOR, '[data-lang="en"]').click()
    assert fee_cell(page, 2, 1).text == "Custom"
    assert fee_cell(page, 2, 1, "resident").text == "Custom"
    assert fee_cell(page, 1, 1).text == "General fee (taxable)"


def test_the_language_choice_is_remembered_after_a_reload(page):
    page.find_element(By.CSS_SELECTOR, '[data-lang="en"]').click()
    page.refresh()
    assert page.execute_script("return document.documentElement.lang") == "en"
    assert "Office Copy" in text_of(page, '[data-copy="office"] h1')


def test_the_sheet_fits_one_page_in_both_languages(page):
    check = """
        const half = document.querySelector('[data-copy="office"]');
        const wide = [...half.querySelectorAll("th, td")].filter((e) => e.scrollWidth > e.clientWidth + 1).length;
        return [half.scrollHeight === half.clientHeight, wide];
    """
    for language in ("ko", "en"):
        page.find_element(By.CSS_SELECTOR, f'[data-lang="{language}"]').click()
        assert page.execute_script(check) == [True, 0], language


def test_both_copies_have_the_same_layout(page):
    tops = """
        return [...document.querySelectorAll('[data-copy="%s"] table, [data-copy="%s"] .sign .row')].map((e) => Math.round(e.getBoundingClientRect().top));
    """
    assert page.execute_script(tops % ("office", "office")) == page.execute_script(tops % ("resident", "resident"))


def test_printing_gives_one_a4_landscape_page(page):
    for language in ("ko", "en"):
        page.find_element(By.CSS_SELECTOR, f'[data-lang="{language}"]').click()
        pdf = base64.b64decode(page.execute_cdp_cmd("Page.printToPDF", {"preferCSSPageSize": True, "printBackground": True})["data"])
        assert len(re.findall(rb"/Type\s*/Page\b(?!s)", pdf)) == 1, language
        width, height = (float(v) for v in re.search(rb"/MediaBox\s*\[\s*0\s+0\s+([\d.]+)\s+([\d.]+)", pdf).groups())
        assert (round(width), round(height)) == (842, 595), language


def test_saved_image_is_the_sheet_at_twice_its_size(page):
    size = page.execute_async_script("""
        const done = arguments[arguments.length - 1];
        renderSheet().then((canvas) => done([canvas.width, canvas.height, canvas.toDataURL("image/png").startsWith("data:image/png")]));
    """)
    sheet = page.execute_script('const r = document.querySelector(".sheet").getBoundingClientRect(); return [r.width, r.height]')
    assert size[2] is True
    assert abs(size[0] - 2 * sheet[0]) <= 2 and abs(size[1] - 2 * sheet[1]) <= 2


def fill_sample(page):
    field(page, "address").send_keys("Room 547")
    field(page, "bank").click()
    type_over(field(page, "bank"), "Bank")
    field(page, "account").send_keys("123-456")
    fee_cell(page, 1, 2).send_keys("46,290")
    type_over(fee_cell(page, 2, 1), "Custom")
    type_over(fee_cell(page, 11, 8), "168,110")
    type_over(fee_cell(page, 13, 8), "31,130")
    meter(page, "전기", 1, "prev").send_keys("19075")
    meter(page, "전기", 1, "curr").send_keys("19329")
    meter(page, "전기", 1, "usage").send_keys("254")


def test_saved_state_holds_the_typed_values(page):
    fill_sample(page)
    state = page.execute_script("return readState()")
    assert state["version"] == 1 and state["language"] == "ko"
    assert state["fields"]["address"] == "Room 547"
    assert state["fields"]["bank"] == "Bank"
    assert state["fields"]["month-total"] == "216,050"
    assert state["fees"][0][0] == {"name": None, "amount": "46,290"}  # a default label is not saved
    assert state["fees"][1][0]["name"] == "Custom"
    electricity = next(m for m in state["meters"] if m["meter"] == "전기" and m["month"] == 1)
    assert (electricity["previous"], electricity["current"], electricity["usage"]) == ("19,075", "19,329", "254")


def test_loading_a_saved_state_restores_both_copies(page):
    fill_sample(page)
    state = page.execute_script("return readState()")
    page.get(PAGE_URL)  # a fresh, empty sheet
    assert field(page, "address").text == ""
    page.execute_script("writeState(arguments[0])", state)
    for copy in ("office", "resident"):
        assert field(page, "address", copy).text == "Room 547"
        assert field(page, "bank", copy).text == "Bank"
        assert fee_cell(page, 1, 2, copy).text == "46,290"
        assert fee_cell(page, 2, 1, copy).text == "Custom"
        assert fee_cell(page, 12, 8, copy).text == "16,810"
        assert field(page, "month-total", copy).text == "216,050"
        assert meter(page, "전기", 1, "usage", copy).text == "254"
    assert meter(page, "전기", 2, "prev").text == "19,329"  # the carried reading is saved and restored too


def test_loading_replaces_what_was_on_the_sheet(page):
    field(page, "address").send_keys("Old")
    fee_cell(page, 3, 2).send_keys("999")
    page.execute_script("writeState(arguments[0])", {"version": 1, "fields": {"address": "New"}})
    assert field(page, "address").text == "New"
    assert fee_cell(page, 3, 2).text == ""
    assert fee_cell(page, 3, 2, "resident").text == ""


def test_default_labels_follow_the_language_a_sheet_is_loaded_in(page):
    page.find_element(By.CSS_SELECTOR, '[data-lang="en"]').click()
    state = page.execute_script("return readState()")
    assert state["language"] == "en" and state["fees"][0][0]["name"] is None and state["fields"]["bank"] is None
    state["language"] = "ko"
    page.execute_script("writeState(arguments[0])", state)
    assert fee_cell(page, 1, 1).text == "일반관리비(과)"
    assert fee_cell(page, 1, 1, "resident").text == "일반관리비(과)"
    assert field(page, "bank").text == "계좌"


def test_a_file_that_is_not_a_saved_sheet_is_refused(page):
    for text in ("not json", "[]", "{}", '{"version": 2, "fields": {}}', '{"version": 1}'):
        assert page.execute_script("return parseState(arguments[0])", text) is None, text
    assert page.execute_script("return parseState(arguments[0]).fields.address", '{"version": 1, "fields": {"address": "x"}}') == "x"


def test_save_button_downloads_the_sheet_as_json(page):
    field(page, "address").send_keys("Room 547")
    page.execute_script("""
        const original = URL.createObjectURL;
        URL.createObjectURL = (blob) => { window.savedBlob = blob; return original(blob); };
    """)
    page.find_element(By.ID, "save-json-btn").click()
    text = page.execute_async_script("const done = arguments[arguments.length - 1]; window.savedBlob.text().then(done);")
    assert json.loads(text)["fields"]["address"] == "Room 547"


def test_load_button_reads_a_json_file(page, tmp_path):
    saved = tmp_path / "sheet.json"
    saved.write_text(json.dumps({"version": 1, "fields": {"address": "From file"}}), encoding="utf-8")
    page.execute_script("document.getElementById('json-file').hidden = false")
    page.find_element(By.ID, "json-file").send_keys(str(saved))
    for _ in range(50):  # the file is read asynchronously
        if field(page, "address").text:
            break
        time.sleep(0.1)
    assert field(page, "address").text == "From file"
    assert field(page, "address", "resident").text == "From file"


def test_settlement_total_is_the_monthly_total_plus_unpaid_and_late_fee(page):
    type_over(fee_cell(page, 11, 8), "168,110")
    type_over(fee_cell(page, 13, 8), "31,130")
    assert field(page, "settle-total").text == "216,050"  # no unpaid amount or late fee yet
    type_over(field(page, "unpaid"), "1,000")
    assert field(page, "settle-total").text == "217,050"
    type_over(field(page, "late-fee"), "500")
    assert field(page, "settle-total").text == "217,550"
    assert field(page, "settle-total", "resident").text == "217,550"
    assert field(page, "settlement").text == "217,550원"
    clear(field(page, "unpaid"))
    assert field(page, "settle-total").text == "216,550"


def test_settlement_total_with_only_an_unpaid_amount(page):
    type_over(field(page, "unpaid"), "2,500")
    assert field(page, "settle-total").text == "2,500"


def test_settlement_total_can_be_typed_over(page):
    type_over(fee_cell(page, 13, 8), "31,130")
    type_over(field(page, "settle-total"), "999")
    assert field(page, "settle-total").text == "999"
    assert field(page, "settlement").text == "999원"
