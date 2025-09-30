import io
import json
import pandas as pd


def read_as_df(body, file_type, encoding_type="utf-8"):
    buffer = io.BytesIO(body)
    if not body.strip():
        return pd.DataFrame()  # handles empty files
    if file_type == "csv":
        if ";" in body.decode(encoding_type, errors="ignore"):
            return pd.read_csv(buffer, sep=";")
        if "\t" in body.decode(encoding_type, errors="ignore"):
            return pd.read_csv(buffer, sep="\t")
        else:
            return pd.read_csv(buffer)

    elif file_type == "json":
        data = json.loads(body.decode(encoding_type))
        if isinstance(data, list):
            return pd.DataFrame(data)
        elif isinstance(data, dict):
            for value in data.values():
                if isinstance(value, list):
                    return pd.DataFrame(value)
            return pd.DataFrame.from_dict(data, orient="index")

    elif file_type == "parquet":
        return pd.read_parquet(buffer, engine="pyarrow")
    else:
        raise ValueError(
            f"Unsupported file type: {file_type}, must be csv, json or parquet"
        )
