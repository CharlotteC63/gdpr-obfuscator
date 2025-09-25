import pandas as pd
import io


def read_data_string_as_df(csv_string):
    if not csv_string:
        return None
    possible_delimiters = [",", ";", "\t", "|"]
    try:
        csv_buffer = io.StringIO(csv_string)
        if (
            "," not in csv_string
            and ";" not in csv_string
            and "\t" not in csv_string
            and "|" not in csv_string
        ):
            if "'" in csv_string:
                return pd.read_csv(csv_buffer, quotechar="'")
            return pd.read_csv(csv_buffer)
        for file_delimiter in possible_delimiters:
            if file_delimiter in csv_string and "'" in csv_string:
                return pd.read_csv(csv_buffer, delimiter=file_delimiter, quotechar="'")
            elif file_delimiter in csv_string:
                return pd.read_csv(csv_buffer, delimiter=file_delimiter)
            else:
                continue
    except Exception as err:
        raise ValueError(
            f"Failed to parse file due to invalid format or unknown delimiter. Details: {err}"
        )
