import json
import re
import shutil
import subprocess

import pytest

from maintenance_bills import cli, generator

# The generated PDFs need Chrome, so these tests are skipped without it.
pytestmark = pytest.mark.usefixtures("browser")

STATE = {
    "version": 1,
    "language": "ko",
    "fields": {"address": "Room 547", "month-total": "216,050", "settle-total": "216,050"},
    "fees": [[{"name": None, "amount": "46,290"}, {"name": "Custom", "amount": ""}, {"name": None, "amount": ""}]],
    "meters": [{"meter": "전기", "month": 1, "previous": "19,075", "current": "19,329", "usage": "254"}],
}


def write_state(tmp_path, state=STATE):
    path = tmp_path / "sheet.json"
    path.write_text(json.dumps(state), encoding="utf-8")
    return str(path)


def pdf_size(path):
    data = open(path, "rb").read()
    pages = len(re.findall(rb"/Type\s*/Page\b(?!s)", data))
    width, height = (float(v) for v in re.search(rb"/MediaBox\s*\[\s*0\s+0\s+([\d.]+)\s+([\d.]+)", data).groups())
    return pages, (round(width), round(height))


def test_generate_writes_one_a4_landscape_page(tmp_path):
    output = tmp_path / "out.pdf"
    assert generator.generate_pdf(json.dumps(STATE), None, str(output)) == str(output)
    assert output.read_bytes().startswith(b"%PDF")
    assert pdf_size(output) == (1, (842, 595))


@pytest.mark.skipif(shutil.which("pdftotext") is None, reason="pdftotext is not installed")
def test_language_option_decides_the_labels_and_keeps_typed_values(tmp_path):
    def text(language):
        output = tmp_path / f"{language}.pdf"
        generator.generate_pdf(json.dumps(STATE), language, str(output))
        return subprocess.run(["pdftotext", str(output), "-"], capture_output=True, text=True).stdout

    english, korean = text("en"), text("ko")
    assert "Office Copy" in english and "Room 547" in english and "Custom" in english
    assert "관리소용" in korean and "Room 547" in korean


def test_cli_generate_prints_the_path_as_json(tmp_path, capsys):
    output = tmp_path / "out.pdf"
    code = cli.main(["generate", "--state-file", write_state(tmp_path), "--language", "en", "--output", str(output)])
    result = json.loads(capsys.readouterr().out)
    assert code == 0 and result == {"ok": True, "data": {"path": str(output)}}
    assert output.exists()


def test_cli_generate_reports_a_missing_file(tmp_path, capsys):
    code = cli.main(["generate", "--state-file", str(tmp_path / "missing.json")])
    result = json.loads(capsys.readouterr().out)
    assert code == 1 and result["ok"] is False and "cannot read" in result["error"]


@pytest.mark.parametrize("text", ["not json", "[]", '{"version": 2, "fields": {}}', '{"version": 1}'])
def test_cli_generate_refuses_a_file_that_is_not_a_saved_sheet(tmp_path, capsys, text):
    path = tmp_path / "bad.json"
    path.write_text(text, encoding="utf-8")
    code = cli.main(["generate", "--state-file", str(path), "--output", str(tmp_path / "out.pdf")])
    result = json.loads(capsys.readouterr().out)
    assert code == 1 and result["ok"] is False and "not a saved sheet" in result["error"]
    assert not (tmp_path / "out.pdf").exists()
