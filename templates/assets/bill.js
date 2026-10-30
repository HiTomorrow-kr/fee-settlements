// The right half is a copy of the left one with only the recipient changed.
const sheet = document.querySelector(".sheet");
const office = sheet.querySelector('[data-copy="office"]');

const feeBody = office.querySelector('[data-field="fees"]');
for (let i = 0; i < 13; i++) {
  feeBody.insertAdjacentHTML("beforeend", "<tr><td></td><td class='num'></td><td class='gap'></td><td></td><td class='num'></td><td class='gap'></td><td></td><td class='num'></td></tr>");
}

// Fixed item names, one list of label keys per column group. An empty string is a blank row.
const FEE_KEYS = [
  [
    "generalFeeTaxable", "securityFee", "cleaningFeeTaxable", "",
    "disinfectionFee", "elevatorUpkeep", "",
    "repairFee", "buildingInsurance", "tvInternet", "generalFeeExempt", "repairFeeTaxable", "",
  ],
  [
    "householdElectricity", "commonElectricity", "elevatorElectricity", "tvLicense", "powerFund", "householdWater", "commonWater", "",
    "householdHeating", "basicHeating", "",
    "householdHotWater", "householdGas",
  ],
  [
    "suspenseReceipt", "parkingFee", "feeSubsidy", "longTermReserve", "committee", "heatingVoucher", "", "", "", "",
    "taxableTotal", "vat", "exemptTotal",
  ],
];
FEE_KEYS.forEach((keys, group) => {
  keys.forEach((key, row) => { if (key) feeBody.rows[row].cells[group * 3].dataset.i18n = key; });
});

const meterBody = office.querySelector('[data-field="meters"]');
// Two meters per row: 전기/수도/가스 on the left, 온수/난방/정수 on the right.
const pairs = [["전기", "온수"], ["수도", "난방"], ["가스", "정수"]];
// The Korean names are the meter ids (they match bill_config.json); the label keys only decide what is shown.
const METER_KEYS = { "전기": "electricity", "수도": "water", "가스": "gas", "온수": "hotWater", "난방": "heating", "정수": "purifiedWater" };
const meterCells = (name, m) => (m === 1 ? `<td rowspan="3" class="cat" data-i18n="${METER_KEYS[name]}"></td>` : "") + `<td data-i18n="month${m}"></td>` + ["prev", "curr", "usage"].map((col) => `<td class="num" data-meter="${name}" data-m="${m}" data-col="${col}"></td>`).join("");
for (const [left, right] of pairs) {
  for (let m = 1; m <= 3; m++) {
    meterBody.insertAdjacentHTML("beforeend", `<tr>${meterCells(left, m)}<td class="gap"></td>${meterCells(right, m)}</tr>`);
  }
}

// Every fillable cell is editable on the left half only; the right half mirrors it.
const EDITABLE = [
  '[data-field="address"]', '[data-field="area"]',
  '[data-field="period"]', '[data-field="month-total"]', '[data-field="unpaid"]', '[data-field="late-fee"]', '[data-field="settle-total"]', '[data-field="out-name"]', '[data-field="out-contact"]',
  '[data-field="in-name"]', '[data-field="in-contact"]', '[data-field="bank"]', '[data-field="account"]', '[data-field="settlement"]',
  '[data-field="fees"] td:not(.gap)', '[data-field="meters"] td.num',
].join(",");
office.querySelectorAll(EDITABLE).forEach((el) => {
  el.setAttribute("contenteditable", "plaintext-only");
  el.addEventListener("keydown", (e) => { if (e.key === "Enter") e.preventDefault(); });
});

// Meter readings take digits and one decimal point, and group the integer part with commas.
const formatReading = (text) => {
  const [int, ...rest] = text.replace(/[^0-9.]/g, "").split(".");
  const grouped = int.replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  return rest.length ? `${grouped}.${rest.join("")}` : grouped;
};
office.querySelectorAll('[data-field="meters"] td.num').forEach((el) => {
  el.addEventListener("beforeinput", (e) => {
    if (e.data && /[^0-9.]/.test(e.data)) e.preventDefault();
  });
  el.addEventListener("input", () => {
    const formatted = formatReading(el.textContent);
    if (formatted === el.textContent) return;
    el.textContent = formatted;
    const sel = getSelection();
    sel.selectAllChildren(el);
    sel.collapseToEnd();
  });
});

// A month's current reading carries into the next month's previous reading, which stays editable.
office.querySelectorAll('[data-col="curr"]').forEach((el) => {
  el.addEventListener("input", () => {
    const next = office.querySelector(`[data-meter="${el.dataset.meter}"][data-m="${+el.dataset.m + 1}"][data-col="prev"]`);
    if (!next) return;
    next.textContent = el.textContent;
    next.dispatchEvent(new Event("input"));
  });
});

// 당월합계 is the sum of 과세합계, 부가세 and 비과세합계 (the last three cells of the rightmost amount column).
const totalParts = [10, 11, 12].map((row) => feeBody.rows[row].cells[7]);
const monthTotal = office.querySelector('[data-field="month-total"]');
const toNumber = (text) => parseFloat(text.replace(/,/g, "")) || 0;
totalParts.forEach((cell) => {
  cell.addEventListener("input", () => {
    const texts = totalParts.map((c) => c.textContent.trim());
    const sum = Math.round(texts.reduce((acc, t) => acc + toNumber(t), 0));
    monthTotal.textContent = texts.every((t) => t === "") ? "" : String(sum).replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    monthTotal.dispatchEvent(new Event("input"));
  });
});

// 부가세 is 10% of 과세합계, rounded to the nearest 10 won; it stays editable.
const [taxable, vat] = totalParts;
taxable.addEventListener("input", () => {
  const text = taxable.textContent.trim();
  vat.textContent = text === "" ? "" : String(Math.round(toNumber(text) * 0.1 / 10) * 10).replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  vat.dispatchEvent(new Event("input"));
});

// 정산금 repeats 정산합계 with the won sign; it stays editable.
const settleTotal = office.querySelector('[data-field="settle-total"]');
const settlement = office.querySelector('[data-field="settlement"]');
settleTotal.addEventListener("input", () => {
  const text = settleTotal.textContent.trim();
  settlement.textContent = text === "" ? "" : `${text}원`;
  settlement.dispatchEvent(new Event("input"));
});

// The settlement total is the monthly total plus the unpaid amount and the late fee; it stays editable.
const settleParts = ["month-total", "unpaid", "late-fee"].map((name) => office.querySelector(`[data-field="${name}"]`));
settleParts.forEach((part) => {
  part.addEventListener("input", () => {
    const texts = settleParts.map((el) => el.textContent.trim());
    const sum = Math.round(texts.reduce((acc, t) => acc + toNumber(t), 0));
    settleTotal.textContent = texts.every((t) => t === "") ? "" : String(sum).replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    settleTotal.dispatchEvent(new Event("input"));
  });
});

const resident = office.cloneNode(true);
resident.dataset.copy = "resident";
resident.querySelector('h1 [data-i18n="copyOffice"]').dataset.i18n = "copyResident";
sheet.appendChild(resident);

const source = office.querySelectorAll(EDITABLE);
const mirror = resident.querySelectorAll(EDITABLE);
mirror.forEach((el) => el.removeAttribute("contenteditable"));
source.forEach((el, i) => el.addEventListener("input", () => { mirror[i].textContent = el.textContent; }));

// Labels in Korean and English. A label is replaced only while it still shows a default text, so typed-over names stay.
const I18N = {
  ko: {
    pageTitle: "중간관리비 정산서", print: "출력", saveImage: "이미지로 저장", saveJson: "JSON 저장", loadJson: "JSON 불러오기", loadError: "JSON 파일을 읽을 수 없습니다.",
    title: "중간관리비", copyOffice: "(관리소용)", copyResident: "(전출자용)", area: "면적 :",
    itemName: "항 목 명", amount: "정산금액", monthTotal: "당월합계", unpaid: "미납금", lateFee: "연체료", settleTotal: "정산합계",
    type: "구분", meteringMonth: "검침월", previous: "전월", current: "당월", usage: "사용량",
    month1: "1개월", month2: "2개월", month3: "3개월",
    electricity: "전기", water: "수도", gas: "가스", hotWater: "온수", heating: "난방", purifiedWater: "정수",
    period: "- 중간관리비 정산기간 :", outName: "전출자 성명", inName: "전입자 성명", seal: "(인)", contact: "연락처 :", bank: "계좌", settlement: "정산금 :",
    generalFeeTaxable: "일반관리비(과)", securityFee: "경비비", cleaningFeeTaxable: "청소비(과)", disinfectionFee: "소독비", elevatorUpkeep: "승강기유지비",
    repairFee: "수선유지비", buildingInsurance: "건물보험료", tvInternet: "TV인터넷사용", generalFeeExempt: "일반관리비(비)", repairFeeTaxable: "수선유지비(과)",
    householdElectricity: "세대전기료", commonElectricity: "공동전기료", elevatorElectricity: "승강기전기", tvLicense: "TV수신료", powerFund: "전력기금",
    householdWater: "세대수도료", commonWater: "공동수도료", householdHeating: "세대난방비", basicHeating: "기본난방비", householdHotWater: "세대급탕비", householdGas: "세대가스료",
    suspenseReceipt: "가수금", parkingFee: "주차비", feeSubsidy: "관리비보조금", longTermReserve: "장기수선충당금", committee: "관리단운영위원", heatingVoucher: "난방바우처",
    taxableTotal: "과세합계", vat: "부가세", exemptTotal: "비과세합계",
  },
  en: {
    pageTitle: "Interim Maintenance Fee Settlement Sheet", print: "Print", saveImage: "Save as image", saveJson: "Save JSON", loadJson: "Load JSON", loadError: "Could not read the JSON file.",
    title: "Interim Maintenance Fee", copyOffice: "(Office Copy)", copyResident: "(Moving-out Resident Copy)", area: "Area :",
    itemName: "Item", amount: "Amount", monthTotal: "Monthly Total", unpaid: "Unpaid", lateFee: "Late Fee", settleTotal: "Settlement Total",
    type: "Type", meteringMonth: "Month", previous: "Previous", current: "Current", usage: "Usage",
    month1: "Month 1", month2: "Month 2", month3: "Month 3",
    electricity: "Electricity", water: "Water", gas: "Gas", hotWater: "Hot Water", heating: "Heating", purifiedWater: "Purified Water",
    period: "- Interim fee settlement period :", outName: "Outgoing resident", inName: "Incoming resident", seal: "(Seal)", contact: "Contact :", bank: "Account", settlement: "Settlement Amount :",
    generalFeeTaxable: "General fee (taxable)", securityFee: "Security fee", cleaningFeeTaxable: "Cleaning fee (taxable)", disinfectionFee: "Disinfection fee", elevatorUpkeep: "Elevator upkeep",
    repairFee: "Repair & upkeep", buildingInsurance: "Building insurance", tvInternet: "TV & internet", generalFeeExempt: "General fee (exempt)", repairFeeTaxable: "Repair & upkeep (taxable)",
    householdElectricity: "Household electricity", commonElectricity: "Common electricity", elevatorElectricity: "Elevator electricity", tvLicense: "TV license fee", powerFund: "Power fund",
    householdWater: "Household water", commonWater: "Common water", householdHeating: "Household heating", basicHeating: "Basic heating", householdHotWater: "Household hot water", householdGas: "Household gas",
    suspenseReceipt: "Suspense receipt", parkingFee: "Parking fee", feeSubsidy: "Fee subsidy", longTermReserve: "Long-term repair reserve", committee: "Management committee", heatingVoucher: "Heating voucher",
    taxableTotal: "Taxable total", vat: "VAT", exemptTotal: "Tax-exempt total",
  },
};
const applyLang = (lang, initial = false) => {
  document.documentElement.lang = lang;
  document.body.classList.toggle("lang-en", lang === "en");
  document.title = I18N[lang].pageTitle;
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const key = el.dataset.i18n;
    const text = el.textContent.trim();
    if (initial || text === I18N.ko[key] || text === I18N.en[key]) el.textContent = I18N[lang][key];
  });
  document.querySelectorAll("[data-lang]").forEach((button) => button.classList.toggle("active", button.dataset.lang === lang));
  try { localStorage.setItem("lang", lang); } catch (e) { /* the choice just is not remembered */ }
};
document.querySelectorAll("[data-lang]").forEach((button) => button.addEventListener("click", () => applyLang(button.dataset.lang)));
let startLang = "ko";
try { startLang = localStorage.getItem("lang") === "en" ? "en" : "ko"; } catch (e) { /* default to Korean */ }
applyLang(startLang, true);

// Saves the typed values as JSON and loads them back, so a finished sheet can be reused.
// A label that still shows its default text is saved as null, so it follows the language it is loaded in.
const FIELD_ORDER = ["address", "area", "period", "month-total", "unpaid", "late-fee", "settle-total", "settlement", "out-name", "out-contact", "in-name", "in-contact", "bank", "account"];
const GROUPS = [0, 1, 2];
const isDefaultLabel = (el) => {
  const key = el.dataset.i18n;
  const text = el.textContent.trim();
  return Boolean(key) && (text === I18N.ko[key] || text === I18N.en[key]);
};
const currentLanguage = () => document.documentElement.lang;
const meterCell = (name, month, column) => office.querySelector(`[data-meter="${name}"][data-m="${month}"][data-col="${column}"]`);

const readState = () => ({
  version: 1,
  language: currentLanguage(),
  fields: Object.fromEntries(FIELD_ORDER.map((name) => {
    const el = office.querySelector(`[data-field="${name}"]`);
    return [name, name === "bank" && isDefaultLabel(el) ? null : el.textContent.trim()];
  })),
  fees: [...feeBody.rows].map((row) => GROUPS.map((group) => ({
    name: isDefaultLabel(row.cells[group * 3]) ? null : row.cells[group * 3].textContent.trim(),
    amount: row.cells[group * 3 + 1].textContent.trim(),
  }))),
  meters: [...office.querySelectorAll('[data-meter][data-col="prev"]')].map((cell) => ({
    meter: cell.dataset.meter,
    month: Number(cell.dataset.m),
    previous: cell.textContent.trim(),
    current: meterCell(cell.dataset.meter, cell.dataset.m, "curr").textContent.trim(),
    usage: meterCell(cell.dataset.meter, cell.dataset.m, "usage").textContent.trim(),
  })),
});

// Returns the parsed state, or null when the text is not a saved sheet.
const parseState = (text) => {
  try {
    const state = JSON.parse(text);
    return state && state.version === 1 && typeof state.fields === "object" && state.fields !== null ? state : null;
  } catch (e) {
    return null;
  }
};

const writeState = (state) => {
  if (state.language === "ko" || state.language === "en") applyLang(state.language);
  const lang = currentLanguage();
  // Every cell is set, in the page's own order, so the calculated cells end up with the saved values.
  const set = (el, text) => { el.textContent = text ?? ""; el.dispatchEvent(new Event("input")); };
  [...feeBody.rows].forEach((row, r) => GROUPS.forEach((group) => {
    const saved = (state.fees && state.fees[r] && state.fees[r][group]) || {};
    const nameCell = row.cells[group * 3];
    set(nameCell, saved.name ?? (nameCell.dataset.i18n ? I18N[lang][nameCell.dataset.i18n] : ""));
    set(row.cells[group * 3 + 1], saved.amount);
  }));
  const savedMeters = state.meters || [];
  office.querySelectorAll('[data-meter][data-col="prev"]').forEach((cell) => {
    const saved = savedMeters.find((m) => m.meter === cell.dataset.meter && m.month === Number(cell.dataset.m)) || {};
    set(cell, saved.previous);
    set(meterCell(cell.dataset.meter, cell.dataset.m, "curr"), saved.current);
    set(meterCell(cell.dataset.meter, cell.dataset.m, "usage"), saved.usage);
  });
  FIELD_ORDER.forEach((name) => {
    const el = office.querySelector(`[data-field="${name}"]`);
    set(el, name === "bank" ? (state.fields.bank ?? I18N[lang].bank) : state.fields[name]);
  });
};

document.getElementById("save-json-btn").addEventListener("click", () => {
  const name = office.querySelector('[data-field="address"]').textContent.trim() || "sheet";
  const link = document.createElement("a");
  link.download = `fee_settlement_${name}.json`;
  link.href = URL.createObjectURL(new Blob([JSON.stringify(readState(), null, 2)], { type: "application/json" }));
  link.click();
});
const jsonFile = document.getElementById("json-file");
document.getElementById("load-json-btn").addEventListener("click", () => jsonFile.click());
jsonFile.addEventListener("change", async () => {
  const file = jsonFile.files[0];
  jsonFile.value = "";
  if (!file) return;
  const state = parseState(await file.text());
  if (state) writeState(state);
  else alert(I18N[currentLanguage()].loadError);
});

// Prints the sheet on one A4 landscape page; the controls are hidden by the print styles.
document.getElementById("print-btn").addEventListener("click", () => {
  if (document.activeElement) document.activeElement.blur();
  window.print();
});

// Saves the two halves as one PNG; the focus outline is dropped so it doesn't end up in the image.
// html2canvas draws every cell's borders itself, so a shared edge is drawn twice and comes out thick.
// For the saved image only, give each edge to one cell (right/bottom, plus left/top where nothing precedes it).
const CAPTURE_CSS = `
  table { border-collapse: separate !important; border-spacing: 0 !important; }
  th, td { border: 0 !important; border-right: 1px solid #000 !important; border-bottom: 1px solid #000 !important; }
  th.gap, td.gap { border: 0 !important; }
  .items tr > :first-child, .items .gap + th, .items .gap + td { border-left: 1px solid #000 !important; }
  .items thead th:not(.gap) { border-top: 1px solid #000 !important; }
  .items tbody tr:last-child td:not(.gap) { border-bottom: 0 !important; }
  .items tfoot tr:first-child td { border-top: 1px solid #000 !important; }
  .items tr.spacer td { border: 0 !important; }
  .items tr.spacer + tr td { border-top: 1px solid #000 !important; }
  .meters thead tr > :first-child, .meters thead .gap + th, .meters td.cat { border-left: 1px solid #000 !important; }
  .meters thead th:not(.gap) { border-top: 1px solid #000 !important; }
`;
const renderSheet = () => {
  if (document.activeElement) document.activeElement.blur();
  return html2canvas(sheet, {
    scale: 2,
    onclone: (doc) => {
      const style = doc.createElement("style");
      style.textContent = CAPTURE_CSS;
      doc.head.appendChild(style);
    },
  });
};
document.getElementById("save-image-btn").addEventListener("click", async () => {
  const canvas = await renderSheet();
  const name = office.querySelector('[data-field="address"]').textContent.trim() || "bill";
  const link = document.createElement("a");
  link.download = `fee_settlement_${name}.png`;
  link.href = canvas.toDataURL("image/png");
  link.click();
});
