# fee-settlements

한국어 | [English](../README.md)

fee-settlements는 관리비 정산서를 작성하고 이미지로 저장한다. 메시징 플랫폼과 무관한 독립 프로그램이라, 어떤 봇(텔레그램, 디스코드 등)이든 서브프로세스로 구동할 수 있다.

## 주요 기능

- 서버 없이 브라우저에서 동작하는 HTML 정산서 페이지 하나
- A4 가로 한 장에 같은 내용의 정산서 두 부: 왼쪽 부에 입력한 내용이 오른쪽 부에 그대로 나타남
- 항목 금액, 검침값, 정산기간, 계좌, 서명란 직접 입력
- 당월합계, 부가세(과세합계의 10%를 10원 단위로 반올림), 정산금 자동 계산, 계산된 칸도 직접 수정 가능
- 천 단위 쉼표가 붙는 검침값, 한 달의 당월 검침값이 다음 달의 전월 검침값으로 이어짐
- 정산서 전체를 페이지 크기의 2배인 PNG 한 장으로 내보내기
- 설치 단계 없음 — Python 3.11+ 환경에서 PYTHONPATH만으로 동작

## 사용법

```bash
python -m maintenance_bills totals --readings-json '[{"name": "<meter name>", "previous": 100, "current": 110}]'
```

모든 명령은 결과를 JSON 한 줄로 stdout에 출력한다: `{"ok": true, "data": ...}` 또는 `{"ok": false, "error": "..."}`, 종료 코드 0/1. 고정 항목 금액과 계량 항목 단가는 bill_config.json에 설정하며, 검침값의 이름은 그 파일의 계량 항목 이름과 같아야 한다.

브라우저에서 정산서를 직접 작성하려면 templates/bill.html을 열고 칸을 눌러 입력한 뒤, 저장 버튼으로 PNG를 내려받는다.

## 연동

오케스트레이터는 이 저장소를 같은 서버에 클론하고 `PYTHONPATH`에 추가한 뒤, `python -m maintenance_bills <command> ...`를 서브프로세스로 실행하고 출력되는 JSON 한 줄을 파싱한다.

## 라이선스

MIT — [LICENSE](../LICENSE) 참고.
