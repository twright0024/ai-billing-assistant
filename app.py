import streamlit as st
import pandas as pd
import io, json, uuid, datetime as dt
import os
from parsers.file_parser import load_invoice_dfs
from exporters.csv_export import to_csv_bytes

os.makedirs("refs", exist_ok=True)

st.set_page_config(page_title="Billing & Freight Audit Assistant (MVP)", layout="wide")
st.title("AI Billing & Freight Audit Assistant — MVP")
st.caption("Upload a FedEx Freight invoice (CSV, XLSX, or PDF).")

# Sidebar tolerance settings
with st.sidebar:
    st.header("Audit Settings")
    abs_tol = st.number_input("Absolute Tolerance ($)", min_value=0.0, value=2.0, step=0.5)
    pct_tol = st.number_input("Percent Tolerance (%)", min_value=0.0, value=1.0, step=0.1)

inv_file = st.file_uploader("Upload Invoice (CSV, XLSX, or PDF)", type=["csv", "xlsx", "pdf"])

if st.button("Parse Invoice", type="primary", disabled=(inv_file is None)):
    try:
        # Parse invoice
        line_items_df, accessorials_df, total_due = load_invoice_dfs(inv_file)

        # Calculate totals
        line_items_total = line_items_df['billed_amount'].sum() if not line_items_df.empty else 0.0
        accessorials_total = accessorials_df['billed_amount'].sum() if not accessorials_df.empty else 0.0
        calculated_total = line_items_total + accessorials_total
        difference = total_due - calculated_total

        # Tolerance check
        tolerance_limit = max(abs_tol, total_due * (pct_tol / 100.0))
        status = "PASS" if abs(difference) <= tolerance_limit else "FLAG"
        status_color = "green" if status == "PASS" else "red"

        # Invoice Summary
        st.subheader("Invoice Summary")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Invoice Total", f"${total_due:,.2f}")
        m2.metric("Calculated Total", f"${calculated_total:,.2f}")
        m3.metric("Difference", f"${difference:,.2f}")
        m4.markdown(f"**Status:** <span style='color:{status_color}; font-weight:bold;'>{status}</span>", unsafe_allow_html=True)

        # Line Items Table
        st.subheader("Line Items")
        st.dataframe(line_items_df)
        st.download_button(
            "Download Line Items CSV",
            data=to_csv_bytes(line_items_df),
            file_name=f"line_items_{uuid.uuid4().hex[:8]}.csv",
            mime="text/csv"
        )

        # Accessorial Charges Table
        st.subheader("Accessorial Charges")
        st.dataframe(accessorials_df)
        st.download_button(
            "Download Accessorials CSV",
            data=to_csv_bytes(accessorials_df),
            file_name=f"accessorials_{uuid.uuid4().hex[:8]}.csv",
            mime="text/csv"
        )

        # Log
        log = {
            "run_id": uuid.uuid4().hex,
            "ts": dt.datetime.utcnow().isoformat(),
            "invoice_total": total_due,
            "calculated_total": calculated_total,
            "difference": difference,
            "status": status,
            "counts": {"line_items": len(line_items_df), "accessorials": len(accessorials_df)}
        }
        with open("refs/parse_log.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(log) + "\n")

    except Exception as e:
        st.error(f"Parsing failed: {e}")