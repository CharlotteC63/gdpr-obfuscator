import pytest
import time
import pandas as pd
import os
import io
from io import BytesIO
import boto3
from moto import mock_aws
from src.obfuscator import Obfuscator
from src.obfuscator import NoPIIFoundInFile


@pytest.fixture(scope="function")
def aws_creds():
    # Mocked aws credentials for moto
    os.environ["AWS_ACCESS_KEY_ID"] = "Test"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "Test"
    os.environ["AWS_SESSION_TOKEN"] = "Test"
    os.environ["AWS_SECURITY_TOKEN"] = "Test"
    os.environ["AWS_DEFAULT_REGION"] = "eu-north-1"


@pytest.fixture(scope="function")
def s3(aws_creds):
    # This fixture yields a mock s3 client using moto, containing a mock s3 bucket.
    with mock_aws():
        yield boto3.client("s3", region_name="eu-north-1")


@pytest.fixture
def bucket(s3):
    s3.create_bucket(
        Bucket="test-bucket",
        CreateBucketConfiguration={"LocationConstraint": "eu-north-1"},
    )
    with open("tests/data/dummy_data_short.csv", "rb") as file1:
        s3.put_object(
            Body=file1, Bucket="test-bucket", Key="new_data/short_test_file.csv"
        )
    with open("tests/data/dummy_data_long.csv", "rb") as file2:
        s3.put_object(
            Body=file2, Bucket="test-bucket", Key="new_data/long_test_file.csv"
        )
    with open("tests/data/dummy_data_short.json", "rb") as file3:
        s3.put_object(
            Body=file3, Bucket="test-bucket", Key="new_data/short_test_file.json"
        )
    with open("tests/data/dummy_data_long.json", "rb") as file4:
        s3.put_object(
            Body=file4, Bucket="test-bucket", Key="new_data/long_test_file.json"
        )
    with open("tests/data/dummy_data_array_format.json", "rb") as file4:
        s3.put_object(
            Body=file4, Bucket="test-bucket", Key="new_data/array_format_test_file.json"
        )
    with open("tests/data/dummy_data_dict_format.json", "rb") as file4:
        s3.put_object(
            Body=file4, Bucket="test-bucket", Key="new_data/dict_format_test_file.json"
        )
    with open("tests/data/dummy_data_short.parquet", "rb") as file5:
        s3.put_object(
            Body=file5, Bucket="test-bucket", Key="new_data/short_test_file.parquet"
        )
    with open("tests/data/dummy_data_long.parquet", "rb") as file6:
        s3.put_object(
            Body=file6, Bucket="test-bucket", Key="new_data/long_test_file.parquet"
        )
    with open("tests/data/dummy_data_utf16.csv", "rb") as file7:
        s3.put_object(
            Body=file7, Bucket="test-bucket", Key="new_data/utf16_test_file.csv"
        )
    with open("tests/data/dummy_data_utf16.json", "rb") as file8:
        s3.put_object(
            Body=file8, Bucket="test-bucket", Key="new_data/utf16_test_file.json"
        )
    with open("tests/data/dummy_data_utf8sig.csv", "rb") as file9:
        s3.put_object(
            Body=file9, Bucket="test-bucket", Key="new_data/utf8sig_test_file.csv"
        )
    with open("tests/data/dummy_data_utf8sig.json", "rb") as file10:
        s3.put_object(
            Body=file10, Bucket="test-bucket", Key="new_data/utf8sig_test_file.json"
        )
    s3.put_object(Body="", Bucket="test-bucket", Key="new_data/empty_test_file.csv")
    s3.put_object(Body="", Bucket="test-bucket", Key="new_data/empty_test_file.json")
    return s3


class TestObfuscatorProperties:
    @pytest.mark.it(
        "Check that the Obfuscator class has the file_to_obfuscate property"
    )
    def test_file_to_obfuscate_property(self, s3, bucket):
        test_obfuscator = Obfuscator(
            "s3://test-bucket/new_data/short_test_file.csv", ["name"]
        )
        assert hasattr(test_obfuscator, "file_to_obfuscate")
        assert (
            test_obfuscator.file_to_obfuscate
            == "s3://test-bucket/new_data/short_test_file.csv"
        )

    @pytest.mark.it("Check that the Obfuscator class has the pii_fields property")
    def test_pii_fields_property(self, s3, bucket):
        test_obfuscator = Obfuscator(
            "s3://test-bucket/new_data/short_test_file.csv", ["name"]
        )
        assert hasattr(test_obfuscator, "pii_fields")
        assert test_obfuscator.pii_fields == ["name"]


class TestGetObfuscatedDFMethod:

    @pytest.mark.it(
        "When file_to_obfuscate attribute is a path to an empty file, raises NoPIIFoundInFile Exception with appropriate message"
    )
    def test_raises_NoPIIFoundInFile_exception_when_file_to_obfuscate_is_empty(
        self, s3, bucket
    ):
        obfuscator = Obfuscator(
            "s3://test-bucket/new_data/empty_test_file.csv", ["name"]
        )
        with pytest.raises(NoPIIFoundInFile) as err:
            obfuscator.get_obfuscated_df()
        assert (
            str(err.value)
            == "The specified PII fields were not found in the specified file"
        )

    @pytest.mark.it(
        "When pii_fields is empty list, raises NoPIIFoundInFile Exception with appropriate message"
    )
    def test_raises_NoPIIFoundInFile_exception_when_pii_fields_is_empty_list(
        self, s3, bucket
    ):
        obfuscator = Obfuscator("s3://test-bucket/new_data/short_test_file.csv", [])
        with pytest.raises(NoPIIFoundInFile) as err:
            obfuscator.get_obfuscated_df()
        assert str(err.value) == "No PII fields have been specified"

    @pytest.mark.it(
        "When pii_fields are not found in file_to_obfuscate, raises NoPIIFoundInFile Exception with appropriate message"
    )
    def test_raises_NoPIIFoundInFile_exception_when_file_to_obfuscate_does_not_contain_specified_pii_fields(
        self, s3, bucket
    ):
        obfuscator = Obfuscator(
            "s3://test-bucket/new_data/short_test_file.csv", ["phone_number"]
        )
        with pytest.raises(NoPIIFoundInFile) as err:
            obfuscator.get_obfuscated_df()
        assert (
            str(err.value)
            == "The file does not contain any of the specified PII fields"
        )

    @pytest.mark.it(
        """When passed with a one-row csv file that contains one pii field, returns a dataframe with the same data
        but with that one pii column obfuscated"""
    )
    def test_returns_correct_dataframe_for_short_csv_file_with_one_pii_field(
        self, s3, bucket
    ):
        obfuscator = Obfuscator(
            "s3://test-bucket/new_data/short_test_file.csv", ["name"]
        )
        obfuscated_df = obfuscator.get_obfuscated_df()
        assert len(obfuscated_df.index) == 1
        assert len(obfuscated_df.columns) == 5
        assert isinstance(obfuscated_df, pd.DataFrame)
        assert obfuscated_df.iloc[0]["name"] == "***"
        assert obfuscated_df.iloc[0]["cohort_graduation_date"] == "2025-03-17"
        assert obfuscated_df.iloc[0]["student_id"] == 1234
        assert obfuscated_df.iloc[0]["course"] == "Software"
        assert obfuscated_df.iloc[0]["email_address"] == "j.smith@email.com"

    @pytest.mark.it(
        """When passed with a one-row csv file that contains two pii fields, returns a dataframe with the same data
        but with those two pii columns obfuscated"""
    )
    def test_returns_correct_dataframe_for_short_csv_file_with_two_pii_fields(
        selfs3, bucket
    ):
        obfuscator = Obfuscator(
            "s3://test-bucket/new_data/short_test_file.csv", ["name", "email_address"]
        )
        obfuscated_df = obfuscator.get_obfuscated_df()
        assert isinstance(obfuscated_df, pd.DataFrame)
        assert len(obfuscated_df.index) == 1
        assert len(obfuscated_df.columns) == 5
        assert obfuscated_df.iloc[0]["name"] == "***"
        assert obfuscated_df.iloc[0]["cohort_graduation_date"] == "2025-03-17"
        assert obfuscated_df.iloc[0]["student_id"] == 1234
        assert obfuscated_df.iloc[0]["course"] == "Software"
        assert obfuscated_df.iloc[0]["email_address"] == "***"

    @pytest.mark.it(
        """When passed with a multiple-row csv file that contains one pii field, returns a dataframe with the same
        data, but with that one pii column obfuscated"""
    )
    def test_returns_correct_dataframe_for_long_csv_file_with_one_pii_field(
        self, s3, bucket
    ):
        obfuscator = Obfuscator(
            "s3://test-bucket/new_data/long_test_file.csv", ["name"]
        )
        obfuscated_df = obfuscator.get_obfuscated_df()
        assert isinstance(obfuscated_df, pd.DataFrame)
        assert len(obfuscated_df.index) == 100
        assert len(obfuscated_df.columns) == 5
        assert obfuscated_df.iloc[0]["name"] == "***"
        assert obfuscated_df.iloc[0]["cohort_graduation_date"] == "2025-03-17"
        assert obfuscated_df.iloc[1]["name"] == "***"
        assert obfuscated_df.iloc[1]["student_id"] == 5678
        assert obfuscated_df.iloc[2]["name"] == "***"
        assert obfuscated_df.iloc[2]["course"] == "Cybersecurity"

    @pytest.mark.it(
        """When passed with a multiple-row csv file that contains two pii fields, returns a dataframe with the same
        data, but with those two pii columns obfuscated"""
    )
    def test_returns_correct_dataframe_for_long_csv_file_with_two_pii_fields_obfuscated(
        self, s3, bucket
    ):
        obfuscator = Obfuscator(
            "s3://test-bucket/new_data/long_test_file.csv", ["name", "email_address"]
        )
        obfuscated_df = obfuscator.get_obfuscated_df()
        assert isinstance(obfuscated_df, pd.DataFrame)
        assert len(obfuscated_df.index) == 100
        assert len(obfuscated_df.columns) == 5
        assert obfuscated_df.iloc[0]["name"] == "***"
        assert obfuscated_df.iloc[0]["cohort_graduation_date"] == "2025-03-17"
        assert obfuscated_df.iloc[0]["email_address"] == "***"
        assert obfuscated_df.iloc[1]["name"] == "***"
        assert obfuscated_df.iloc[1]["student_id"] == 5678
        assert obfuscated_df.iloc[1]["email_address"] == "***"
        assert obfuscated_df.iloc[2]["name"] == "***"
        assert obfuscated_df.iloc[2]["course"] == "Cybersecurity"
        assert obfuscated_df.iloc[3]["email_address"] == "***"

    @pytest.mark.it(
        """When passed with a one-row json file that contains one pii field, returns a dataframe with the same data
        but with that one pii column obscufated"""
    )
    def test_returns_correct_dataframe_for_short_json_file_with_one_pii_field(
        self, s3, bucket
    ):
        obfuscator = Obfuscator(
            "s3://test-bucket/new_data/short_test_file.json", ["name"]
        )
        obfuscated_df = obfuscator.get_obfuscated_df()
        assert len(obfuscated_df.index) == 1
        assert len(obfuscated_df.columns) == 5
        assert isinstance(obfuscated_df, pd.DataFrame)
        assert obfuscated_df.iloc[0]["name"] == "***"
        assert obfuscated_df.iloc[0]["cohort_graduation_date"] == "2025-03-17"
        assert obfuscated_df.iloc[0]["student_id"] == 1234
        assert obfuscated_df.iloc[0]["course"] == "Software"
        assert obfuscated_df.iloc[0]["email_address"] == "j.smith@email.com"

    @pytest.mark.it(
        """When passed with a one-row json file that contains two pii fields, returns a dataframe with the same data
        but with those two pii columns obscufated"""
    )
    def test_returns_correct_dataframe_for_short_json_file_with_two_pii_fields(
        selfs3, bucket
    ):
        obfuscator = Obfuscator(
            "s3://test-bucket/new_data/short_test_file.json", ["name", "email_address"]
        )
        obfuscated_df = obfuscator.get_obfuscated_df()
        assert isinstance(obfuscated_df, pd.DataFrame)
        assert len(obfuscated_df.index) == 1
        assert len(obfuscated_df.columns) == 5
        assert obfuscated_df.iloc[0]["name"] == "***"
        assert obfuscated_df.iloc[0]["cohort_graduation_date"] == "2025-03-17"
        assert obfuscated_df.iloc[0]["student_id"] == 1234
        assert obfuscated_df.iloc[0]["course"] == "Software"
        assert obfuscated_df.iloc[0]["email_address"] == "***"

    @pytest.mark.it(
        """When passed with a multiple-row json file that contains one pii field, returns a dataframe with the same
        data, but with that one pii column obfuscated"""
    )
    def test_returns_correct_dataframe_for_long_json_file_with_one_pii_field(
        self, s3, bucket
    ):
        obfuscator = Obfuscator(
            "s3://test-bucket/new_data/long_test_file.json", ["name"]
        )
        obfuscated_df = obfuscator.get_obfuscated_df()
        assert isinstance(obfuscated_df, pd.DataFrame)
        assert len(obfuscated_df.index) == 2
        assert len(obfuscated_df.columns) == 5
        assert obfuscated_df.iloc[0]["student_id"] == 1234
        assert obfuscated_df.iloc[0]["name"] == "***"
        assert obfuscated_df.iloc[0]["cohort_graduation_date"] == "2025-03-17"
        assert obfuscated_df.iloc[0]["course"] == "Software"
        assert obfuscated_df.iloc[0]["email_address"] == "j.smith@email.com"
        assert obfuscated_df.iloc[1]["student_id"] == 2222
        assert obfuscated_df.iloc[1]["name"] == "***"
        assert obfuscated_df.iloc[1]["cohort_graduation_date"] == "2025-03-17"
        assert obfuscated_df.iloc[1]["course"] == "Software"
        assert obfuscated_df.iloc[1]["email_address"] == "j.doe@email.com"

    @pytest.mark.it(
        """When passed with a multiple-row json file that contains two pii fields, returns a dataframe with the same
        data, but with those pii columns obfuscated"""
    )
    def test_returns_multiple_row_dataframe_with_two_pii_fields_obfuscated(
        self, s3, bucket
    ):
        obfuscator = Obfuscator(
            "s3://test-bucket/new_data/long_test_file.json", ["name", "email_address"]
        )
        obfuscated_df = obfuscator.get_obfuscated_df()
        assert isinstance(obfuscated_df, pd.DataFrame)
        assert len(obfuscated_df.index) == 2
        assert len(obfuscated_df.columns) == 5
        assert obfuscated_df.iloc[0]["name"] == "***"
        assert obfuscated_df.iloc[0]["cohort_graduation_date"] == "2025-03-17"
        assert obfuscated_df.iloc[0]["email_address"] == "***"
        assert obfuscated_df.iloc[1]["name"] == "***"
        assert obfuscated_df.iloc[1]["student_id"] == 2222
        assert obfuscated_df.iloc[1]["email_address"] == "***"

    @pytest.mark.it(
        """When passed with a json file with an array format, returns correctly obfuscated
        dataframe"""
    )
    def test_returns_correct_dataframe_for_json_file_formatted_as_an_array_with_one_pii_field(
        self, s3, bucket
    ):
        obfuscator = Obfuscator(
            "s3://test-bucket/new_data/array_format_test_file.json", ["name"]
        )
        obfuscated_df = obfuscator.get_obfuscated_df()
        assert isinstance(obfuscated_df, pd.DataFrame)
        assert len(obfuscated_df.index) == 1
        assert len(obfuscated_df.columns) == 5
        assert obfuscated_df.iloc[0]["student_id"] == 1234
        assert obfuscated_df.iloc[0]["name"] == "***"
        assert obfuscated_df.iloc[0]["course"] == "Software"
        assert obfuscated_df.iloc[0]["cohort_graduation_date"] == "2025-03-17"
        assert obfuscated_df.iloc[0]["email_address"] == "j.smith@email.com"

    @pytest.mark.it(
        """When passed with a json file with a single dict format, returns correctly obfuscated
        dataframe"""
    )
    def test_returns_correct_dataframe_for_json_file_formatted_as_single_dict_with_one_pii_field(
        self, s3, bucket
    ):
        obfuscator = Obfuscator(
            "s3://test-bucket/new_data/dict_format_test_file.json", ["name"]
        )
        obfuscated_df = obfuscator.get_obfuscated_df()
        assert isinstance(obfuscated_df, pd.DataFrame)
        assert len(obfuscated_df.index) == 1
        assert len(obfuscated_df.columns) == 5
        assert obfuscated_df.iloc[0]["student_id"] == 1234
        assert obfuscated_df.iloc[0]["name"] == "***"
        assert obfuscated_df.iloc[0]["course"] == "Software"
        assert obfuscated_df.iloc[0]["cohort_graduation_date"] == "2025-03-17"
        assert obfuscated_df.iloc[0]["email_address"] == "j.smith@email.com"

    @pytest.mark.it(
        "When passed with a short (one record) parquet file with one PII field, returns correctly obfuscated dataframe"
    )
    def test_returns_correct_dataframe_for_short_parquet_file_with_one_pii_field(
        self, s3, bucket
    ):
        obfuscator = Obfuscator(
            "s3://test-bucket/new_data/short_test_file.parquet", ["name"]
        )
        obfuscated_df = obfuscator.get_obfuscated_df()
        assert isinstance(obfuscated_df, pd.DataFrame)
        assert len(obfuscated_df.index) == 1
        assert len(obfuscated_df.columns) == 5
        assert obfuscated_df.iloc[0]["student_id"] == 1234
        assert obfuscated_df.iloc[0]["name"] == "***"
        assert obfuscated_df.iloc[0]["course"] == "Software"
        assert obfuscated_df.iloc[0]["cohort_graduation_date"] == "2025-03-17"
        assert obfuscated_df.iloc[0]["email_address"] == "j.smith@email.com"

    @pytest.mark.it(
        "When passed with a longer (multiple record) parquet file with one PII field, returns correctly obfuscated dataframe"
    )
    def test_returns_correct_dataframe_for_long_parquet_file_with_one_pii_field(
        self, s3, bucket
    ):
        obfuscator = Obfuscator(
            "s3://test-bucket/new_data/long_test_file.parquet", ["name"]
        )
        obfuscated_df = obfuscator.get_obfuscated_df()
        assert isinstance(obfuscated_df, pd.DataFrame)
        assert len(obfuscated_df.index) == 3
        assert len(obfuscated_df.columns) == 5
        assert obfuscated_df.iloc[0]["student_id"] == 1234
        assert obfuscated_df.iloc[0]["name"] == "***"
        assert obfuscated_df.iloc[0]["course"] == "Software"
        assert obfuscated_df.iloc[0]["cohort_graduation_date"] == "2025-03-17"
        assert obfuscated_df.iloc[0]["email_address"] == "j.smith@email.com"
        assert obfuscated_df.iloc[1]["student_id"] == 5678
        assert obfuscated_df.iloc[1]["name"] == "***"
        assert obfuscated_df.iloc[1]["course"] == "Software"
        assert obfuscated_df.iloc[1]["cohort_graduation_date"] == "2025-03-17"
        assert obfuscated_df.iloc[1]["email_address"] == "j.doe@email.com"
        assert obfuscated_df.iloc[2]["student_id"] == 9101
        assert obfuscated_df.iloc[2]["name"] == "***"
        assert obfuscated_df.iloc[2]["course"] == "Cybersecurity"
        assert obfuscated_df.iloc[2]["cohort_graduation_date"] == "2025-03-17"
        assert obfuscated_df.iloc[2]["email_address"] == "a.johnson@email.com"

    @pytest.mark.it(
        "When passed with a longer (multiple record) parquet file with two PII fields, returns correctly obfuscated dataframe"
    )
    def test_returns_correct_dataframe_for_long_parquet_file_with_two_pii_fields(
        self, s3, bucket
    ):
        obfuscator = Obfuscator(
            "s3://test-bucket/new_data/long_test_file.parquet",
            ["name", "email_address"],
        )
        obfuscated_df = obfuscator.get_obfuscated_df()
        assert isinstance(obfuscated_df, pd.DataFrame)
        assert len(obfuscated_df.index) == 3
        assert len(obfuscated_df.columns) == 5
        assert obfuscated_df.iloc[0]["student_id"] == 1234
        assert obfuscated_df.iloc[0]["name"] == "***"
        assert obfuscated_df.iloc[0]["course"] == "Software"
        assert obfuscated_df.iloc[0]["cohort_graduation_date"] == "2025-03-17"
        assert obfuscated_df.iloc[0]["email_address"] == "***"
        assert obfuscated_df.iloc[1]["student_id"] == 5678
        assert obfuscated_df.iloc[1]["name"] == "***"
        assert obfuscated_df.iloc[1]["course"] == "Software"
        assert obfuscated_df.iloc[1]["cohort_graduation_date"] == "2025-03-17"
        assert obfuscated_df.iloc[1]["email_address"] == "***"
        assert obfuscated_df.iloc[2]["student_id"] == 9101
        assert obfuscated_df.iloc[2]["name"] == "***"
        assert obfuscated_df.iloc[2]["course"] == "Cybersecurity"
        assert obfuscated_df.iloc[2]["cohort_graduation_date"] == "2025-03-17"
        assert obfuscated_df.iloc[2]["email_address"] == "***"


class TestGetObfuscatedBytestreamMethod:

    @pytest.mark.it(
        "Raises TypeError with appropriate message when passed with any object other than a dataframe"
    )
    def test_raises_TypeError_when_passed_with_object_that_is_not_dataframe(
        self, s3, bucket
    ):
        obfuscator = Obfuscator(
            "s3://test-bucket/new_data/short_test_file.csv", ["name", "email_address"]
        )
        with pytest.raises(TypeError) as err:
            obfuscator.get_obfuscated_bytestream([])
        assert str(err.value) == "Expected dataframe but received <class 'list'>"

    @pytest.mark.it("Returns a bytestream type object when passed with a dataframe")
    def test_returns_bytestream_type_object_when_passed_with_dataframe(
        self, s3, bucket
    ):
        obfuscator = Obfuscator(
            "s3://test-bucket/new_data/short_test_file.csv", ["name", "email_address"]
        )
        test_dataframe = obfuscator.get_obfuscated_df()
        assert isinstance(test_dataframe, pd.DataFrame)
        result = obfuscator.get_obfuscated_bytestream(test_dataframe)
        assert isinstance(result, io.BytesIO)

    @pytest.mark.it(
        "When passed with a dataframe, with original file_type as csv, and encoding_type as utf-8, returns correct bytestream"
    )
    def test_csv_output_utf8_returns_bytestream(self, s3, bucket):
        obfuscator = Obfuscator(
            "s3://test-bucket/new_data/short_test_file.csv", ["name", "email_address"]
        )
        test_dataframe = obfuscator.get_obfuscated_df()
        result = obfuscator.get_obfuscated_bytestream(test_dataframe)
        assert isinstance(result, io.BytesIO)
        contents = result.getvalue().decode("utf-8")
        assert "student_id" in contents
        assert "1234" in contents
        assert "name" in contents
        assert "***" in contents
        assert "course" in contents
        assert "Software" in contents
        assert "cohort_graduation_date" in contents
        assert "2025-03-17" in contents
        assert "email_address" in contents
        assert "***" in contents

    @pytest.mark.it(
        "When passed with a dataframe, with original file_type as json, and encoding_type as utf-8, returns correct bytestream"
    )
    def test_json_output_utf8_returns_bytestream(self, s3, bucket):
        obfuscator = Obfuscator(
            "s3://test-bucket/new_data/short_test_file.json", ["name", "email_address"]
        )
        test_dataframe = obfuscator.get_obfuscated_df()
        result = obfuscator.get_obfuscated_bytestream(test_dataframe)
        assert isinstance(result, io.BytesIO)
        contents = result.getvalue().decode("utf-8")
        assert "student_id" in contents
        assert "1234" in contents
        assert "name" in contents
        assert "***" in contents
        assert "course" in contents
        assert "Software" in contents
        assert "cohort_graduation_date" in contents
        assert "2025-03-17" in contents
        assert "email_address" in contents
        assert "***" in contents

    @pytest.mark.it(
        "When passed with a dataframe, with original file_type as parquet, returns correct bytestream"
    )
    def test_parquet_output_returns_bytestream_with_correct_contents_when_decoded(
        self, s3, bucket
    ):
        obfuscator = Obfuscator(
            "s3://test-bucket/new_data/short_test_file.parquet",
            ["name", "email_address"],
        )
        test_dataframe = obfuscator.get_obfuscated_df()
        result = obfuscator.get_obfuscated_bytestream(test_dataframe)
        assert isinstance(result, bytes)
        contents = pd.read_parquet(BytesIO(result), engine="pyarrow")
        assert "student_id" in contents.columns
        assert contents["student_id"].iloc[0] == 1234
        assert "name" in contents.columns
        assert contents["name"].iloc[0] == "***"
        assert "course" in contents.columns
        assert contents["course"].iloc[0] == "Software"
        assert "cohort_graduation_date" in contents.columns
        assert contents["cohort_graduation_date"].iloc[0] == "2025-03-17"
        assert "email_address" in contents.columns
        assert contents["email_address"].iloc[0] == "***"

    @pytest.mark.it(
        "Bytestream object returned is compatible with boto3 S3 Put Object, when original file is csv"
    )
    def test_returns_bytestream_type_object_compatible_with_boto3_s3_putobject_when_original_file_is_csv(
        self, s3, bucket
    ):
        obfuscator = Obfuscator(
            "s3://test-bucket/new_data/short_test_file.csv", ["name", "email_address"]
        )
        obfuscated_df = obfuscator.get_obfuscated_df()
        obfuscated_bytestream = obfuscator.get_obfuscated_bytestream(obfuscated_df)
        s3.put_object(
            Body=obfuscated_bytestream,
            Bucket="test-bucket",
            Key="obfuscated_data/short_test_file.csv",
        )
        response = s3.list_objects_v2(
            Bucket="test-bucket", Prefix="obfuscated_data/short_test_file.csv"
        )
        assert "Contents" in response
        keys = [obj["Key"] for obj in response["Contents"]]
        assert "obfuscated_data/short_test_file.csv" in keys

    @pytest.mark.it(
        "Bytestream object returned is compatible with boto3 S3 Put Object, when original file is json"
    )
    def test_returns_bytestream_type_object_compatible_with_boto3_s3_putobject_when_original_file_is_json(
        self, s3, bucket
    ):
        obfuscator = Obfuscator(
            "s3://test-bucket/new_data/short_test_file.json", ["name", "email_address"]
        )
        obfuscated_df = obfuscator.get_obfuscated_df()
        obfuscated_bytestream = obfuscator.get_obfuscated_bytestream(obfuscated_df)
        s3.put_object(
            Body=obfuscated_bytestream,
            Bucket="test-bucket",
            Key="obfuscated_data/short_test_file.json",
        )
        response = s3.list_objects_v2(
            Bucket="test-bucket", Prefix="obfuscated_data/short_test_file.json"
        )
        assert "Contents" in response
        keys = [obj["Key"] for obj in response["Contents"]]
        assert "obfuscated_data/short_test_file.json" in keys

    @pytest.mark.it(
        "Bytestream object returned is compatible with boto3 S3 Put Object, when original file is parquet"
    )
    def test_returns_bytestream_type_object_compatible_with_boto3_s3_putobject_when_original_file_is_parquet(
        self, s3, bucket
    ):
        obfuscator = Obfuscator(
            "s3://test-bucket/new_data/short_test_file.parquet",
            ["name", "email_address"],
        )
        obfuscated_df = obfuscator.get_obfuscated_df()
        obfuscated_bytestream = obfuscator.get_obfuscated_bytestream(obfuscated_df)
        s3.put_object(
            Body=obfuscated_bytestream,
            Bucket="test-bucket",
            Key="obfuscated_data/short_test_file.parquet",
        )
        response = s3.list_objects_v2(
            Bucket="test-bucket", Prefix="obfuscated_data/short_test_file.parquet"
        )
        assert "Contents" in response
        keys = [obj["Key"] for obj in response["Contents"]]
        assert "obfuscated_data/short_test_file.parquet" in keys


class TestObfuscatorRuntime:

    @pytest.mark.it(
        "Obfuscator module can handle obfuscating a 1 mb file and returning the bytestream in under 60 seconds"
    )
    def test_obfuscator_handles_a_1mb_file_in_under_60_seconds(self, s3, bucket):
        head = s3.head_object(Bucket="test-bucket", Key="new_data/long_test_file.csv")
        file_size_bytes = head["ContentLength"]
        max_time = (file_size_bytes / 1000000) * 60.0
        start = time.perf_counter()
        obfuscator = Obfuscator(
            "s3://test-bucket/new_data/long_test_file.csv",
            ["name", "email_address"],
        )
        obfuscated_df = obfuscator.get_obfuscated_df()
        obfuscator.get_obfuscated_bytestream(obfuscated_df)
        duration = time.perf_counter() - start
        assert duration < max_time


class TestIntegrationOfUtilFunctions:

    @pytest.mark.it("When passed with a utf-16 encoded csv file, returns correct bytestream containing obfuscated data")
    def test_returns_correct_bytestream_for_utf16_encoded_csv_file(self, s3, bucket):
        obfuscator = Obfuscator(
            "s3://test-bucket/new_data/utf16_test_file.csv",
            ["name", "email_address"],
        )
        assert obfuscator._encoding_type == "utf-16"
        obfuscated_df = obfuscator.get_obfuscated_df()
        obfuscated_bytestream = obfuscator.get_obfuscated_bytestream(obfuscated_df)
        assert isinstance(obfuscated_bytestream, io.BytesIO)
        contents = obfuscated_bytestream.getvalue().decode("utf-16")
        assert "student_id" in contents
        assert "1234" in contents
        assert "name" in contents
        assert "***" in contents
        assert "course" in contents
        assert "Software" in contents
        assert "cohort_graduation_date" in contents
        assert "2025-03-17" in contents
        assert "email_address" in contents
        assert "***" in contents

    @pytest.mark.it("When passed with a utf-16 encoded json file, returns correct bytestream containing obfuscated data")
    def test_returns_correct_bytestream_for_utf16_encoded_json_file(self, s3, bucket):
        obfuscator = Obfuscator(
            "s3://test-bucket/new_data/utf16_test_file.json",
            ["name", "email_address"],
        )
        assert obfuscator._encoding_type == "utf-16"
        obfuscated_df = obfuscator.get_obfuscated_df()
        obfuscated_bytestream = obfuscator.get_obfuscated_bytestream(obfuscated_df)
        assert isinstance(obfuscated_bytestream, io.BytesIO)
        contents = obfuscated_bytestream.getvalue().decode("utf-16")
        assert "student_id" in contents
        assert "1234" in contents
        assert "name" in contents
        assert "***" in contents
        assert "course" in contents
        assert "Software" in contents
        assert "cohort_graduation_date" in contents
        assert "2025-03-17" in contents
        assert "email_address" in contents
        assert "***" in contents

    @pytest.mark.it("When passed with a utf-8-sig encoded csv file, returns correct bytestream containing obfuscated data")
    def test_returns_correct_bytestream_for_utf16_encoded_csv_file(self, s3, bucket):
        obfuscator = Obfuscator(
            "s3://test-bucket/new_data/utf8sig_test_file.csv",
            ["name", "email_address"],
        )
        assert obfuscator._encoding_type == "utf-8-sig"
        obfuscated_df = obfuscator.get_obfuscated_df()
        obfuscated_bytestream = obfuscator.get_obfuscated_bytestream(obfuscated_df)
        assert isinstance(obfuscated_bytestream, io.BytesIO)
        contents = obfuscated_bytestream.getvalue().decode("utf-8-sig")
        assert "student_id" in contents
        assert "1234" in contents
        assert "name" in contents
        assert "***" in contents
        assert "course" in contents
        assert "Software" in contents
        assert "cohort_graduation_date" in contents
        assert "2025-03-17" in contents
        assert "email_address" in contents
        assert "***" in contents

    @pytest.mark.it("When passed with a utf-8-sig encoded json file, returns correct bytestream containing obfuscated data")
    def test_returns_correct_bytestream_for_utf16_encoded_json_file(self, s3, bucket):
        obfuscator = Obfuscator(
            "s3://test-bucket/new_data/utf8sig_test_file.json",
            ["name", "email_address"],
        )
        assert obfuscator._encoding_type == "utf-8-sig"
        obfuscated_df = obfuscator.get_obfuscated_df()
        obfuscated_bytestream = obfuscator.get_obfuscated_bytestream(obfuscated_df)
        assert isinstance(obfuscated_bytestream, io.BytesIO)
        contents = obfuscated_bytestream.getvalue().decode("utf-8-sig")
        assert "student_id" in contents
        assert "1234" in contents
        assert "name" in contents
        assert "***" in contents
        assert "course" in contents
        assert "Software" in contents
        assert "cohort_graduation_date" in contents
        assert "2025-03-17" in contents
        assert "email_address" in contents
        assert "***" in contents
    
    @pytest.mark.it("When passed with an invalid bucket name, raises appropriate error")
    def test_raises_appropriate_error_with_invalid_bucket_name(self, s3, bucket):
        with pytest.raises(ValueError) as err:
            Obfuscator(
                "s3://test_bucket/new_data/short_test_file.parquet",
                ["name", "email_address"],
            )
        assert (
            str(err.value)
            == "Invalid bucket name according to AWS rules, see https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucketnamingrules.html"
        )

    @pytest.mark.it(
        "When passed with an unsupported file format, raises appropriate error"
    )
    def test_raises_appropriate_error_with_unsupported_file_format(self, s3, bucket):
        with pytest.raises(ValueError) as err:
            Obfuscator(
                "s3://test-bucket/new_data/short_test_file.txt",
                ["name", "email_address"],
            )
        assert (
            str(err.value) == "file_type not supported (must be csv, json or parquet)"
        )


# class TestObfuscatorModuleSize:

#     @pytest.mark.it(
#         "Obfuscator module size must not exceed memory limits for Python Lambda dependencies"
#     )
#     def test_obfuscator_module_size_does_not_exceed_memory_limits_for_python_lambda_dependencies(
#         self, s3, bucket
#     ):
#         ## THIS TEST NEEDS COMPLETING
#         package_dir = "lambda_package"
#         zipped_path = "lambda_package.zip"

#         unzipped_size = get_directory_size(package_dir)
#         zipped_size = os.path.getsize(zipped_path)

#         assert unzipped_size <= 250 * 1024 * 1024, f"Unzipped size {unzipped_size/1024**2:.2f}MB exceeds 250MB limit"
#         assert zipped_size <= 50 * 1024 * 1024, f"Zipped size {zipped_size/1024**2:.2f}MB exceeds 50MB direct-upload limit"
