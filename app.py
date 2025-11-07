import io
import pandas as pd
import streamlit as st

from parsers.file_parser import load_invoice_dfs  # uses the unified-return parser

st.set_page_config(page_title="AI Billing & Freight Audit Assistant", layout="wide")
st.title("AI Billing & Freight Audit Assistant — MVP")

def df_to_csv_bytes(df: pd.DataFrame) -> bytes:
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    return buf.getvalue().encode("utf-8")

uploaded = st.file_uploader(
    "Upload a FedEx Freight invoice (PDF / CSV / XLSX)",
    type=["pdf", "csv", "xlsx"]
)

if uploaded:
    st.info(f"Processing: **{uploaded.name}**")
    result = load_invoice_dfs(uploaded)  # always returns dict now

    base_fuel_df     = result.get("base_fuel", pd.DataFrame())
    accessorials_df  = result.get("accessorials", pd.DataFrame())
    adjustments_df   = result.get("adjustments", pd.DataFrame())
    excluded_df      = result.get("excluded", pd.DataFrame())
    totals           = result.get("totals", {}) or {}
    full_with_flags  = result.get("full_with_flags", None)  # may be None depending on your parser

    # Summary tiles
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Base",            f"${totals.get('base', 0):,.2f}")
    c2.metric("Fuel",            f"${totals.get('fuel', 0):,.2f}")
    c3.metric("Accessorials",    f"${totals.get('accessorials', 0):,.2f}")
    c4.metric("Adjustments",     f"${totals.get('adjustments', 0):,.2f}")
    c5.metric("Grand (Included)",f"${totals.get('grand_included', 0):,.2f}")

    st.divider()

    # Tabs
    t1, t2, t3 = st.tabs(["Base & Fuel", "Accessorials", "Adjustments"])

    with t1:
        st.subheader("Base & Fuel")
        if base_fuel_df.empty:
            st.caption("No base/fuel lines detected.")
        else:
            st.dataframe(base_fuel_df, use_container_width=True)
            st.download_button(
                "Download Base & Fuel (CSV)",
                df_to_csv_bytes(base_fuel_df),
                file_name="base_fuel.csv",
                mime="text/csv",
            )

    with t2:
        st.subheader("Accessorial Charges")
        if accessorials_df.empty:
            st.caption("No accessorials detected.")
        else:
            st.dataframe(accessorials_df, use_container_width=True)
            st.download_button(
                "Download Accessorials (CSV)",
                df_to_csv_bytes(accessorials_df),
                file_name="accessorials.csv",
                mime="text/csv",
            )

    with t3:
        st.subheader("Adjustments / Credits")
        if adjustments_df.empty:
            st.caption("No adjustments detected.")
        else:
            st.dataframe(adjustments_df, use_container_width=True)
            st.download_button(
                "Download Adjustments (CSV)",
                df_to_csv_bytes(adjustments_df),
                file_name="adjustments.csv",
                mime="text/csv",
            )

    # Excluded lines (for audit)
    with st.expander("Excluded lines (why)"):
        if excluded_df.empty:
            st.caption("No excluded lines.")
        else:
            st.dataframe(excluded_df, use_container_width=True)
            st.download_button(
                "Download Excluded (CSV)",
                df_to_csv_bytes(excluded_df),
                file_name="excluded.csv",
                mime="text/csv",
            )

    # Optional full export with flags, if your parser includes it
    if isinstance(full_with_flags, pd.DataFrame) and not full_with_flags.empty:
        st.divider()
        st.subheader("Export: Full Parsed Lines (with flags)")
        st.download_button(
            "Download Full (CSV)",
            df_to_csv_bytes(full_with_flags),
            file_name="full_with_flags.csv",
            mime="text/csv",
        )
