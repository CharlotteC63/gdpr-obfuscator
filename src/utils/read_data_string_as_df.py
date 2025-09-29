import pandas as pd
import io
import json


def read_data_string_as_df(data_string, file_type):
    if not data_string:
        return None
    if file_type == "csv":
        possible_delimiters = [",", ";", "\t", "|"]
        try:
            csv_buffer = io.StringIO(data_string)
            if (
                "," not in data_string
                and ";" not in data_string
                and "\t" not in data_string
                and "|" not in data_string
            ):
                if "'" in data_string:
                    return pd.read_csv(csv_buffer, quotechar="'")
                return pd.read_csv(csv_buffer)
            for file_delimiter in possible_delimiters:
                if file_delimiter in data_string and "'" in data_string:
                    return pd.read_csv(
                        csv_buffer, delimiter=file_delimiter, quotechar="'"
                    )
                elif file_delimiter in data_string:
                    return pd.read_csv(csv_buffer, delimiter=file_delimiter)
                else:
                    continue
        except Exception as err:
            raise ValueError(
                f"Failed to parse csv file due to invalid format or unknown delimiter. Details: {err}"
            )

    if file_type == "json":
        try:
            data = json.loads(data_string)
            data_as_list_of_dicts = None
            if isinstance(data, dict):
                dict_values = list(data.values())
                if dict_values:
                    first_value = dict_values[0]
                    if isinstance(first_value, dict):
                        data_as_list_of_dicts = [first_value]
                    elif isinstance(first_value, list):
                        data_as_list_of_dicts = first_value
            elif isinstance(data, list):
                data_as_list_of_dicts = data
            return pd.DataFrame(data_as_list_of_dicts)
        except ValueError:
            raise ValueError("Unsupported json structure")

    if file_type == "parquet":
        pass
