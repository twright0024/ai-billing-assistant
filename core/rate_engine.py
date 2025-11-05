def run_audit(invoice_df, rate_table_df, accessorial_df=None, fuel_mode="percent", fuel_pct=24.0, tolerance=None):
    """
    Placeholder audit logic:
    - Compares billed vs expected based on a simple rule.
    - Returns meta, line items, and totals.
    """
    lines = []
    billed_total = 0.0
    expected_total = 0.0

    for _, row in invoice_df.iterrows():
        billed = row.get("Billed Amount", 0.0)
        expected = billed * 0.95  # Dummy logic: assume 5% discount
        variance = billed - expected

        lines.append({
            "Invoice #": row.get("Invoice #", "N/A"),
            "Billed": billed,
            "Expected": expected,
            "Variance": variance
        })

        billed_total += billed
        expected_total += expected

    totals = {
        "billed_total": billed_total,
        "expected_total": expected_total,
        "variance_total": billed_total - expected_total
    }

    return {"meta": {"fuel_mode": fuel_mode}, "lines": lines, "totals": totals}
