def df_to_string(obfuscated_df, file_type):
    """
    Takes a dataframe and returns a csv data string, json data string, or parquet bytes,
    depending on the original file format.

    Parameters
    ----------
    obfuscated_df : dataframe
        A dataframe containing a file's data, where pii has already been obfuscated.
    file_type: str
        A string identifying the original filetype (csv, json or parquet).

    Returns
    ----------
    str
        A string of the dataframe's contents, in csv, json or parquet format.

    """
    if obfuscated_df.empty:
        return ""
    else:
        if file_type == "csv":
            return obfuscated_df.to_csv(lineterminator="\n", index=False)
        if file_type == "json":
            data_as_dicts = obfuscated_df.to_dict(orient="records")
            return "{'records':" + f"{data_as_dicts}" + "}"
        if file_type == "parquet":
            return obfuscated_df.to_parquet(engine="pyarrow", index=False)
        else:
            raise ValueError("file_type not supported (must be csv, json or parquet)")
