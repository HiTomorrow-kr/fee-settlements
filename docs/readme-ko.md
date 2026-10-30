# fee-settlements

한국어 | [English](../README.md)

fee-settlements는 관리비 정산서를 작성하고 PNG나 PDF로 내보낸다.

## 주요 기능

- 서버 없이 브라우저에서 정산서 작성
- 당월합계, 부가세, 정산금 자동 계산
- 정산서를 PNG로 내보내거나, 저장한 정산서를 A4 가로 PDF로 인쇄

## 시작하기

```bash
git clone https://github.com/HiTomorrow-kr/fee-settlements.git
cd fee-settlements
pip install -e .
```

## 사용법

정산서를 직접 작성하려면 브라우저에서 templates/bill.html을 열고 칸을 눌러 입력한 뒤, 저장 버튼으로 PNG를 내려받는다.

명령줄에서 합계를 계산하거나 저장한 정산서를 인쇄하려면 다음을 실행한다.

```bash
python -m fee_settlements totals --readings-json '[{"name": "<meter name>", "previous": 100, "current": 110}]'
python -m fee_settlements generate --state-file sheet.json --language en --output sheet.pdf
```

- 고정 항목 금액과 계량 항목 단가는 bill_config.json에 설정한다. 검침값의 이름은 그 파일의 계량 항목 이름과 같아야 한다.
- `generate`는 JSON 저장 버튼으로 저장한 정산서를 인쇄한다. Chrome이 필요하다.

## 라이선스

MIT — [LICENSE](../LICENSE) 참고.
