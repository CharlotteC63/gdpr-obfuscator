import io
import boto3
import pandas as pd
import os

if 'LAMBDA_TASK_ROOT' in os.environ:
    # Running in Lambda (deployment)
    from utils.detect_encoding import detect_encoding
    from utils.get_bucket_name import get_bucket_name
    from utils.get_file_key import get_file_key
    from utils.get_file_name_and_type_from_key import get_file_name_and_type_from_key
    from utils.read_as_df import read_as_df
else:
    # Running locally (dev)
    from src.utils.detect_encoding import detect_encoding
    from src.utils.get_bucket_name import get_bucket_name
    from src.utils.get_file_key import get_file_key
    from src.utils.get_file_name_and_type_from_key import get_file_name_and_type_from_key
    from src.utils.read_as_df import read_as_df


class NoPIIFoundInFile(Exception):
    pass


class Obfuscator:
    """
    A class used to represent a file saved in an s3 bucket that may contain PII.

    Attributes
    ----------
    file_to_obfuscate: str
        The s3 path to the file to be obfuscated.
    pii_fields: list
        The list of PII fields to be obfuscated.
    bucket_name: str
        The name of the s3 bucket where the file is located.
    file_name: str
        The name of the file (without the file type extension).
    _file_key: str
        The key of the file in the s3 bucket.
    _file_type: str
        The file type of the file (e.g. csv, json, parquet).
    __file_contents_bytes: bytes
        The contents of the file as bytes, a private attribute as it may contain encoded PII.
    _encoding_type: str
        The encoding type of the file (e.g. utf-8, utf-16, ISO-8859-1).
    __file_contents_df: pd.DataFrame
        The contents of the file as a pandas dataframe, a private attribute as it may contain PII.

    Methods
    -------
    get_obfuscated_df
        Prints and returns an obfuscated pandas dataframe of the file's contents.

    get_obfuscated_bytestream
        Returns a bytestream of the obfuscated file contents, compatible with S3 PutObject.

    """

    def __init__(self, file_to_obfuscate: str = "", pii_fields: list = None):
        """
        Parameters
        ----------
        file_to_obfuscate : str
            The s3 path to the file.
        pii_fields : list
            The fields containing personally identifiable information (PII).
        """
        self.file_to_obfuscate = file_to_obfuscate
        self.pii_fields = pii_fields
        self.bucket_name = get_bucket_name(file_to_obfuscate)
        self.file_name = get_file_name_and_type_from_key(file_to_obfuscate)["name"]
        self._file_key = get_file_key(file_to_obfuscate)
        self._file_type = get_file_name_and_type_from_key(file_to_obfuscate)[
            "file_type"
        ]
        self.__file_contents_bytes = (
            boto3.client("s3")
            .get_object(Bucket=self.bucket_name, Key=self._file_key)["Body"]
            .read()
        )
        self._encoding_type = detect_encoding(self.__file_contents_bytes)
        self.__file_contents_df = read_as_df(
            self.__file_contents_bytes, self._file_type, self._encoding_type
        )

    def get_obfuscated_df(self, obfuscator_string: str = "***") -> pd.DataFrame:
        """Prints a pandas dataframe of the file's contents with PII columns obfuscated.

        If the argument `obfuscator_string` isn't passed in, the default obfuscator
        string is used ('***').

        Parameters
        ----------
        obfuscator_string : str, optional
            The character string that will replace PII (default is "***").

        Returns
        ----------
        pd.DataFrame
            A copy of the file contents in a dataframe, with columns containing PII obfuscated.
        """
        if self.__file_contents_df.empty:
            raise NoPIIFoundInFile(
                "The specified PII fields were not found in the specified file"
            )
        if not self.pii_fields:
            raise NoPIIFoundInFile("No PII fields have been specified")
        contains_pii = False
        file_contents_copy_df = self.__file_contents_df.copy()
        for pii_field in self.pii_fields:
            if pii_field in file_contents_copy_df.columns:
                contains_pii = True
                file_contents_copy_df[pii_field] = obfuscator_string
        if contains_pii is False:
            raise NoPIIFoundInFile(
                "The file does not contain any of the specified PII fields"
            )
        print(file_contents_copy_df)
        return file_contents_copy_df

    def get_obfuscated_bytestream(self, obfuscated_df: pd.DataFrame) -> io.BytesIO:
        """Returns a binary stream (io.BytesIO) for all supported file types (csv, json and parquet), in the chosen encoding
        (utf-8 used as default).

        Parameters
        ----------
        obfuscated_df : DataFrame
            A pandas dataframe containing data to be converted to bytestream.

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
        if not isinstance(obfuscated_df, pd.DataFrame):
            raise TypeError(f"Expected dataframe but received {type(obfuscated_df)}")

        if obfuscated_df.empty:
            raise ValueError("Dataframe cannot be empty")

        if self._file_type not in ("csv", "json", "parquet"):
            raise ValueError(
                f"File type, {self._file_type}, is not supported, must be csv, json or parquet"
            )

        if self._file_type == "parquet":
            buffer = (
                io.BytesIO()
            )  # creates an in-memory binary buffer to hold the parquet file
            obfuscated_df.to_parquet(
                buffer, engine="fastparquet", index=False
            )  # writes the dataframe to the buffer in parquet format using fastparquet
            buffer.seek(
                0
            )  # resets the cursor to the beginning of the buffer, so it can be read from the start
            return buffer.getvalue()  # returns the bytestream

        elif self._file_type == "csv":
            text_buffer = (
                io.StringIO()
            )  # creates an in-memory text buffer to hold the csv file
            obfuscated_df.to_csv(
                text_buffer, index=False
            )  # write the DataFrame to a string buffer in csv format, without the index column
            buffer = (
                io.BytesIO()
            )  # creates an in-memory binary buffer to hold the bytestream
            buffer.write(
                text_buffer.getvalue().encode(self._encoding_type)
            )  # encodes the csv string to bytes which are written onto the buffer
            buffer.seek(
                0
            )  # resets the cursor to the beginning of the buffer, so it can be read from the start
            return buffer  # returns the bytestream

        elif self._file_type == "json":
            text_buffer = (
                io.StringIO()
            )  # creates an in-memory text buffer to hold the json file
            obfuscated_df.to_json(
                text_buffer, orient="records"
            )  # writes the DataFrame to the buffer as a list of records (dicts)
            buffer = (
                io.BytesIO()
            )  # creates an in-memory binary buffer to hold the bytestream
            buffer.write(
                text_buffer.getvalue().encode(self._encoding_type)
            )  # encodes the json string to bytes which are written onto the buffer
            buffer.seek(
                0
            )  # resets the cursor to the beginning of the buffer, so it can be read from the start
            return buffer  # returns the bytestream

        else:
            raise ValueError(f"Unsupported format: {self._file_type}")
