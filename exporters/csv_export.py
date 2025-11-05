def to_csv_bytes(df):
    """
    Converts DataFrame to CSV bytes for download.
    """
    return df.to_csv(index=False).encode("utf-8")
