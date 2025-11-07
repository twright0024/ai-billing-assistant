import pandas as pd
import pdfplumber
import pytesseract
import re
from dataclasses import dataclass

# =====================
# Charge classification
# =====================

BASE = "base_freight"
FUEL = "fuel_surcharge"
ACC  = "accessorial"
ADJ  = "adjustment"
TAX  = "tax_fee"
OTHER= "other"

SUMMARY_PAT = re.compile(r"(sub\s*total|subtotal|total|amount\s*due|invoice\s*amount|balance|remittance|please\s*pay)", re.I)
FUEL_PAT    = re.compile(r"\b(fuel\s*surch(?:arge)?|fsc|fuel\s*surch\.)\b", re.I)
BASE_PAT    = re.compile(r"\b(base|freight\s*charge|linehaul|line\s*haul|lh|store\s*fix(?:ture)?s?)\b", re.I)
TAX_PAT     = re.compile(r"\b(tax|sales\s*tax)\b", re.I)
ADJ_PAT     = re.compile(r"\b(discount|credit|adj(?:ustment)?|rebate)\b", re.I)
EXTRA_INFO  = re.compile(r"\b(FAK|EZONE|PZONE|tariff|original\s+(revenue|weight)|dimension|density|pcf|inspecting\s+terminal|inspection)\b", re.I)

ACCESSORIAL_MAP = [
    (re.compile(r"\bresidential(\s+delivery)?\b", re.I),  "residential_delivery"),
    (re.compile(r"\blift[\s\-]?gate\b", re.I),            "liftgate"),
    (re.compile(r"\blimited\s*access\b", re.I),           "limited_access"),
    (re.compile(r"\bappointment|appt\b", re.I),           "appointment"),
    (re.compile(r"\binside\s*delivery\b", re.I),          "inside_delivery"),
    (re.compile(r"\bredeliver(y)?(\s*charge|\s*chg)?\b", re.I), "redelivery"),
    (re.compile(r"\breweigh\b", re.I),                    "reweigh"),
    (re.compile(r"\breclass\b", re.I),                    "reclass"),
    (re.compile(r"\boverlength|extreme\s*length|>\s*96", re.I), "overlength"),
    (re.compile(r"\bhazmat|hazardous\b", re.I),           "hazmat"),
    (re.compile(r"\bdetention\b", re.I),                  "detention"),
    (re.compile(r"\bstorage\b", re.I),                    "storage"),
    (re.compile(r"\bcorrection\s*fee\b", re.I),          "correction_fee"),
    (re.compile(r"\bweight\s*validation\s*fee\b", re.I),  "weight_validation"),
]

@dataclass
class ChargeRow:
    desc: str
    amount: float
    norm_type: str = ""
    norm_subtype: str = ""
    include: bool = True
    reason: str = ""

def _normalize_row(row: ChargeRow) -> ChargeRow:
    d = (row.desc or "").strip()
    if SUMMARY_PAT.search(d):
        row.include = False; row.reason = "summary_line"; row.norm_type = OTHER; return row
    if EXTRA_INFO.search(d):
        row.include = False; row.reason = "info_note"; row.norm_type = OTHER; return row
    if FUEL_PAT.search(d):
        row.norm_type, row.norm_subtype = FUEL, "fuel"; return row
    if TAX_PAT.search(d):
        row.norm_type, row.norm_subtype = TAX, "tax"; return row
    if ADJ_PAT.search(d) or (row.amount < 0):
        row.norm_type, row.norm_subtype = ADJ, "credit_or_discount"; return row
    if BASE_PAT.search(d):
        row.norm_type, row.norm_subtype = BASE, "base"; return row
    for pat, sub in ACCESSORIAL_MAP:
        if pat.search(d):
            row.norm_type, row.norm_subtype = ACC, sub; return row
    row.norm_type = OTHER; return row

def _apply_rules(rows: list[ChargeRow]) -> list[ChargeRow]:
    rows = [_normalize_row(r) for r in rows]
    # Deduplicate fuel/accessorials by (type, subtype, amount)
    seen = set()
    for r in rows:
        if not r.include: 
            continue
        if r.norm_type in (FUEL, ACC):
            key = (r.norm_type, r.norm_subtype, round(r.amount, 2))
            if key in seen:
                r.include = False; r.reason = "possible_duplicate"
            else:
                seen.add(key)
    # Exclude zero amounts (mark waived for accessorials)
    for r in rows:
        if r.include and abs(r.amount) < 1e-8:
            r.include = False
            r.reason = "waived_accessorial" if r.norm_type == ACC else "zero_amount_excluded"
    # Ensure single base (keep largest)
    base_idxs = [i for i, r in enumerate(rows) if r.include and r.norm_type == BASE]
    if len(base_idxs) > 1:
        largest_i = max(base_idxs, key=lambda i: (rows[i].amount))
        for i in base_idxs:
            if i != largest_i:
                rows[i].include = False; rows[i].reason = "duplicate_base"
    return rows

def validate_and_split(df_lines: pd.DataFrame):
    df = df_lines.copy()
    if "description" not in df.columns:
        raise ValueError("Expected 'description' column")
    if "amount" not in df.columns:
        df["amount"] = 0.0

    rows = [ChargeRow(str(d), float(a)) for d, a in zip(df["description"], df["amount"])]
    rows = _apply_rules(rows)
    out = pd.DataFrame([r.__dict__ for r in rows])

    base_fuel    = out[(out["include"]) & (out["norm_type"].isin([BASE, FUEL]))].copy()
    accessorials = out[(out["include"]) & (out["norm_type"] == ACC)].copy()
    adjustments  = out[(out["include"]) & (out["norm_type"] == ADJ)].copy()
    excluded     = out[~out["include"]].copy()

    totals = {
        "base": round(base_fuel.loc[base_fuel["norm_type"] == BASE, "amount"].sum(), 2),
        "fuel": round(base_fuel.loc[base_fuel["norm_type"] == FUEL, "amount"].sum(), 2),
        "accessorials": round(accessorials["amount"].sum(), 2),
        "adjustments": round(adjustments["amount"].sum(), 2),
    }
    totals["grand_included"] = round(sum(totals.values()), 2)

    # Also return full_with_flags for CSV export if desired
    return base_fuel, accessorials, adjustments, excluded, totals, out

# =====================
# Unified loader
# =====================

def load_invoice_dfs(uploaded_file):
    """Load any supported file and return a unified dict of DataFrames."""
    # CSV/XLSX path
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith('.xlsx'):
        df = pd.read_excel(uploaded_file)
    elif uploaded_file.name.endswith('.pdf'):
        return parse_pdf(uploaded_file)  # handle PDFs separately
    else:
        raise ValueError("Unsupported file format. Please upload CSV, XLSX, or PDF.")

    # Normalize columns for CSV/XLSX
    if not {"description", "amount"}.issubset(df.columns):
        rename_map = {}
        for col in df.columns:
            lower = str(col).lower()
            if ("desc" in lower) or ("type" in lower):
                rename_map[col] = "description"
            elif ("amt" in lower) or ("billed" in lower) or ("amount" in lower):
                rename_map[col] = "amount"
        if rename_map:
            df = df.rename(columns=rename_map)
    if not {"description", "amount"}.issubset(df.columns):
        # Fallback: take first and last columns as description/amount
        df["description"] = df.iloc[:, 0].astype(str)
        df["amount"] = pd.to_numeric(df.iloc[:, -1], errors="coerce").fillna(0.0)

    base_fuel, accessorials, adjustments, excluded, totals, full_with_flags = validate_and_split(df)

    return {
        "base_fuel": base_fuel,
        "accessorials": accessorials,
        "adjustments": adjustments,
        "excluded": excluded,
        "totals": totals,
        "full_with_flags": full_with_flags,
    }

# =====================
# PDF parser
# =====================

def parse_pdf(uploaded_file):
    """Parse FedEx Freight invoice PDFs into a unified dict of DataFrames."""
    text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
            else:
                # OCR fallback
                img = page.to_image(resolution=300).original
                text += pytesseract.image_to_string(img) + "\n"

    # --- Build rows line-by-line, taking ONLY the rightmost 2-decimal number as the amount ---
    data = []
    money_pat = re.compile(r"(\$?\d[\d,]*\.\d{2})(?!\d)")  # two-decimal currency, rightmost in line
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue

        # Find all 2-decimal numbers (treat as money), pick the rightmost
        m = list(money_pat.finditer(line))
        if not m:
            continue

        amount_str = m[-1].group(1)
        desc = line[:m[-1].start()].strip()
        desc = re.sub(r"\s{2,}", " ", desc)  # collapse multiple spaces

        try:
            amt = float(amount_str.replace("$", "").replace(",", ""))
        except ValueError:
            continue

        data.append({"description": desc, "amount": amt})

    if not data:
        return {
            "base_fuel": pd.DataFrame(),
            "accessorials": pd.DataFrame(),
            "adjustments": pd.DataFrame(),
            "excluded": pd.DataFrame(),
            "totals": {"base": 0.0, "fuel": 0.0, "accessorials": 0.0, "adjustments": 0.0, "grand_included": 0.0},
            "full_with_flags": pd.DataFrame(),
        }

    df_lines = pd.DataFrame(data)
    base_fuel, accessorials, adjustments, excluded, totals, full_with_flags = validate_and_split(df_lines)

    return {
        "base_fuel": base_fuel,
        "accessorials": accessorials,
        "adjustments": adjustments,
        "excluded": excluded,
        "totals": totals,
        "full_with_flags": full_with_flags,
    }
