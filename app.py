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

inv_file = st.file_uploader("Upload Invoice (CSV, XLSX, or PDF)", type=["csv", "xlsx", "pdf"])

if st.button("Parse Invoice", type="primary", disabled=(inv_file is None)):
    try:
        line_items_df, accessorials_df, total_due = load_invoice_dfs(inv_file)

        st.subheader("Invoice Summary")
        st.metric("Total Amount Due", f"${total_due:,.2f}")

        st.subheader("Line Items")
        st.dataframe(line_items_df)
        st.download_button(
            "Download Line Items CSV",
            data=to_csv_bytes(line_items_df),
            file_name=f"line_items_{uuid.uuid4().hex[:8]}.csv",
            mime="text/csv"
        )

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
            "total_due": total_due,
            "counts": {"line_items": len(line_items_df), "accessorials": len(accessorials_df)}
        }
        with open("refs/parse_log.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(log) + "\n")

    except Exception as e:
        st.error(f"Parsing failed: {e}")