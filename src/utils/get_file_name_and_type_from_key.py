def get_file_name_and_type_from_key(key: str):
    """
    Extracts the name of a file, and its format type (csv, json or parquet) from a key.

    Parameters
    ----------
    key : str
        The key of a file to be obfuscated within an s3 bucket.

    Returns
    ----------
    dict
        A dictionary with two keys: name (str) and file_type (str).

    Raises
    ----------
    ValueError
        If the key contains a file that is of any format other than csv, json or parquet.

    """
    split_by_slash = key.split("/")
    name = split_by_slash[len(split_by_slash) - 1]
    split_by_period = key.split(".")
    file_type = split_by_period[len(split_by_period) - 1]
    if file_type in ("csv", "json", "parquet"):
        return {"name": name, "file_type": file_type}
    else:
        raise ValueError("file_type not supported (must be csv, json or parquet)")
