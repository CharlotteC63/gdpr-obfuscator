import io
import json
import pandas as pd


def read_as_df(body, file_type, encoding_type="utf-8"):
    """
    Gets the key of an S3 object from its file path.

    Parameters
    ----------
    body : bytes
        The contents of a file in bytes.
    file_type : str
        The formatting type of the file (csv, json or parquet).
    encoding_type : str
        The encoding type of the file (utf-8, utf-16, utf-8-sig, ISO-8859-1, cp1252 and utf-3)

    Returns
    ----------
    pd.DataFrame
        A dataframe of the file's contents.

    Raises
    ----------
    ValueError
        If the file_type is unsupported (supported file types include csv, json and parquet).

    """
    buffer = io.BytesIO(body)
    if not body.strip():
        return pd.DataFrame()  # handles empty files
    if file_type == "csv":
        if ";" in body.decode(encoding_type, errors="ignore"):
            return pd.read_csv(buffer, sep=";", encoding=encoding_type)
        if "\t" in body.decode(encoding_type, errors="ignore"):
            return pd.read_csv(buffer, sep="\t", encoding=encoding_type)
        else:
            return pd.read_csv(buffer, encoding=encoding_type)

    elif file_type == "json":
        data = json.loads(body.decode(encoding_type))
        if isinstance(data, list):
            return pd.DataFrame(data)
        elif isinstance(data, dict):
            for value in data.values():
                if isinstance(value, list):
                    return pd.DataFrame(value)
                if not isinstance(value, list):
                    return pd.DataFrame([data])
            return pd.DataFrame.from_dict(data, orient="index")

    elif file_type == "parquet":
        return pd.read_parquet(buffer, engine="pyarrow")
    else:
        raise ValueError(
            f"Unsupported file type: {file_type}, must be csv, json or parquet"
        )
