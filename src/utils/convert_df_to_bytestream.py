import io
import pandas as pd


def convert_df_to_bytestream(
    data_df: pd.DataFrame, file_type: str, encoding_type: str = "utf-8"
):
    """
    Returns a binary stream (io.BytesIO) for all supported file types (csv, json and parquet), in the chosen encoding
    (utf-8 used as default).

    Parameters
    ----------
    data_df : DataFrame
        A pandas dataframe containing data to be converted to bytestream.

    file_type : str
        A string of the file type (e.g. "csv", "json" or "parquet")

    encoding_type : str
        Default value is "utf-8".

    Returns
    ----------
    io.BytesIO
        A binary stream of the file content in the chosen encoding and file format.

    Raises
    ----------
    ValueError
        - When data is passed in any object other than a datafame.
        - When file_type is passed as a falsy value (such as None or an empty string).
        - When passed with a file_type that is not supported (only "csv", "json" and "parquet" are supported).

    """
    if not isinstance(data_df, pd.DataFrame):
        raise TypeError(f"Expected dataframe but received {type(data_df)}")

    if not file_type:
        raise ValueError("File type cannot be empty")

    if file_type not in ("csv", "json", "parquet"):
        raise ValueError(
            f"File type, {file_type}, is not supported, must be csv, json or parquet"
        )

    if file_type == "parquet":
        buffer = (
            io.BytesIO()
        )  # creates an in-memory binary buffer to hold the parquet file
        data_df.to_parquet(
            buffer, engine="pyarrow", index=False
        )  # writes the dataframe to the buffer in parquet format using pyarrow
        buffer.seek(
            0
        )  # resets the cursor to the beginning of the buffer, so it can be read from the start
        return buffer.getvalue()  # returns the bytestream

    elif file_type == "csv":
        text_buffer = (
            io.StringIO()
        )  # creates an in-memory text buffer to hold the csv file
        data_df.to_csv(
            text_buffer, index=False
        )  # write the DataFrame to a string buffer in csv format, without the index column
        buffer = (
            io.BytesIO()
        )  # creates an in-memory binary buffer to hold the bytestream
        buffer.write(
            text_buffer.getvalue().encode(encoding_type)
        )  # encodes the csv string to bytes which are written onto the buffer
        buffer.seek(
            0
        )  # resets the cursor to the beginning of the buffer, so it can be read from the start
        return buffer  # returns the bytestream

    elif file_type == "json":
        text_buffer = (
            io.StringIO()
        )  # creates an in-memory text buffer to hold the json file
        data_df.to_json(
            text_buffer, orient="records"
        )  # writes the DataFrame to the buffer as a list of records (dicts)
        buffer = (
            io.BytesIO()
        )  # creates an in-memory binary buffer to hold the bytestream
        buffer.write(
            text_buffer.getvalue().encode(encoding_type)
        )  # encodes the json string to bytes which are written onto the buffer
        buffer.seek(
            0
        )  # resets the cursor to the beginning of the buffer, so it can be read from the start
        return buffer  # returns the bytestream

    else:
        raise ValueError(f"Unsupported format: {file_type}")
