import os
import io
import boto3
import pytest
import pandas as pd
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
    s3.put_object(Body="", Bucket="test-bucket", Key="new_data/empty_test_file.csv")
    s3.put_object(Body="", Bucket="test-bucket", Key="new_data/empty_test_file.json")
    return s3

class TestObfuscatorProperties:
    @pytest.mark.it('Check that the Obfuscator class has the file_to_obfuscate property')
    @mock_aws
    def test_file_to_obfuscate_property(self,s3,bucket):
        test_obfuscator = Obfuscator("s3://test-bucket/new_data/short_test_file.csv",["name"])
        assert hasattr(test_obfuscator, "file_to_obfuscate")
        assert test_obfuscator.file_to_obfuscate == "s3://test-bucket/new_data/short_test_file.csv"

    @pytest.mark.it('Check that the Obfuscator class has the pii_fields property')
    @mock_aws
    def test_pii_fields_property(self,s3,bucket):
        test_obfuscator = Obfuscator("s3://test-bucket/new_data/short_test_file.csv",["name"])
        assert hasattr(test_obfuscator, "pii_fields")
        assert test_obfuscator.pii_fields == ["name"]


class TestGetObfuscatedDFMethod:
    
    @pytest.mark.it("When file_to_obfuscate attribute is a path to an empty file, raises NoPIIFoundInFile Exception with appropriate message")
    @mock_aws
    def test_raises_NoPIIFoundInFile_exception_when_file_to_obfuscate_is_empty(self,s3,bucket):
        obfuscator = Obfuscator('s3://test-bucket/new_data/empty_test_file.csv',["name"])
        with pytest.raises(NoPIIFoundInFile) as err:
            obfuscator.get_obfuscated_df()
        assert str(err.value) == "The specified PII fields were not found in the specified file"
    
    @pytest.mark.it("When pii_fields is empty list, raises NoPIIFoundInFile Exception with appropriate message")
    @mock_aws
    def test_raises_NoPIIFoundInFile_exception_when_pii_fields_is_empty_list(self,s3,bucket):
        obfuscator = Obfuscator('s3://test-bucket/new_data/short_test_file.csv',[])
        with pytest.raises(NoPIIFoundInFile) as err:
            obfuscator.get_obfuscated_df()
        assert str(err.value) == "No PII fields have been specified"

    @pytest.mark.it("When pii_fields are not found in file_to_obfuscate, raises NoPIIFoundInFile Exception with appropriate message")
    @mock_aws
    def test_raises_NoPIIFoundInFile_exception_when_file_to_obfuscate_does_not_contain_specified_pii_fields(self,s3,bucket):
        obfuscator = Obfuscator('s3://test-bucket/new_data/short_test_file.csv',['phone_number'])
        with pytest.raises(NoPIIFoundInFile) as err:
            obfuscator.get_obfuscated_df()
        assert str(err.value) == "The file does not contain any of the specified PII fields"

    @pytest.mark.it(
        """When passed with a one-row csv file that contains one pii field, returns a dataframe with the same data
        but with those two pii columns obscufated"""
    )
    @mock_aws
    def test_returns_correct_dataframe_for_short_csv_file_with_one_pii_field(self,s3,bucket):
        obfuscator = Obfuscator('s3://test-bucket/new_data/short_test_file.csv',['name'])
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
        but with those two pii columns obscufated"""
    )
    @mock_aws
    def test_returns_correct_dataframe_for_short_csv_file_with_two_pii_fields(
        selfs3,bucket
    ):
        obfuscator = Obfuscator("s3://test-bucket/new_data/short_test_file.csv",["name","email_address"])
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
        data, but with that pii column obfuscated"""
    )
    @mock_aws
    def test_returns_correct_dataframe_for_long_csv_file_with_one_pii_field(
        self,s3,bucket
    ):
        obfuscator = Obfuscator("s3://test-bucket/new_data/long_test_file.csv",["name"])
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
        data, but with those pii columns obfuscated"""
    )
    @mock_aws
    def test_returns_multiple_row_dataframe_with_one_pii_field_obfuscated(
        self,s3,bucket
    ):
        obfuscator = Obfuscator("s3://test-bucket/new_data/long_test_file.csv",["name","email_address"])
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
        but with that pii column obscufated"""
    )
    @mock_aws
    def test_returns_correct_dataframe_for_short_csv_file_with_one_pii_field(self,s3,bucket):
        obfuscator = Obfuscator('s3://test-bucket/new_data/short_test_file.json',['name'])
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
    @mock_aws
    def test_returns_correct_dataframe_for_short_json_file_with_two_pii_fields(
        selfs3,bucket
    ):
        obfuscator = Obfuscator("s3://test-bucket/new_data/short_test_file.json",["name","email_address"])
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
        data, but with that pii column obfuscated"""
    )
    @mock_aws
    def test_returns_correct_dataframe_for_long_csv_file_with_one_pii_field(
        self,s3,bucket
    ):
        obfuscator = Obfuscator("s3://test-bucket/new_data/long_test_file.json",["name"])
        obfuscated_df = obfuscator.get_obfuscated_df()
        assert isinstance(obfuscated_df, pd.DataFrame)
        assert len(obfuscated_df.index) == 2 # CHECK THIS
        assert len(obfuscated_df.columns) == 6 # CHECK THIS
        assert obfuscated_df.iloc[0]["name"] == "***"
        assert obfuscated_df.iloc[0]["cohort_graduation_date"] == "2025-03-17"
        assert obfuscated_df.iloc[1]["name"] == "***"
        assert obfuscated_df.iloc[1]["student_id"] == 2222
        # ADD MORE ASSERTIONS HERE

    @pytest.mark.it(
        """When passed with a multiple-row json file that contains two pii fields, returns a dataframe with the same
        data, but with those pii columns obfuscated"""
    )
    @mock_aws
    def test_returns_multiple_row_dataframe_with_one_pii_field_obfuscated(
        self,s3,bucket
    ):
        obfuscator = Obfuscator("s3://test-bucket/new_data/long_test_file.json",["name","email_address"])
        obfuscated_df = obfuscator.get_obfuscated_df()
        assert isinstance(obfuscated_df, pd.DataFrame)
        assert len(obfuscated_df.index) == 2 # CHECK THIS
        assert len(obfuscated_df.columns) == 6 # CHECK THIS
        assert obfuscated_df.iloc[0]["name"] == "***"
        assert obfuscated_df.iloc[0]["cohort_graduation_date"] == "2025-03-17"
        assert obfuscated_df.iloc[0]["email_address"] == "***"
        assert obfuscated_df.iloc[1]["name"] == "***"
        assert obfuscated_df.iloc[1]["student_id"] == 2222
        assert obfuscated_df.iloc[1]["email_address"] == "***"
        # ADD MORE ASSERTIONS HERE

# TEST WITH DIFFERENT JSON FORMAT TYPES
# TEST WITH PARQUET


class TestGetObfuscatedBytestreamMethod:

    @pytest.mark.it(
        "Raises TypeError with appropriate message when passed with any object other than a dataframe"
    )
    @mock_aws
    def test_raises_TypeError_when_passed_with_object_that_is_not_dataframe(self,s3,bucket):
        obfuscator = Obfuscator("s3://test-bucket/new_data/short_test_file.csv",["name","email_address"])
        with pytest.raises(TypeError) as err:
            obfuscator.get_obfuscated_bytestream([])
        assert str(err.value) == "Expected dataframe but received <class 'list'>"

    @pytest.mark.it(
        "Returns a bytestream type object when passed with a dataframe"
    )
    @mock_aws
    def test_returns_bytestream_type_object_when_passed_with_dataframe(self,s3,bucket):
        obfuscator = Obfuscator("s3://test-bucket/new_data/short_test_file.csv",["name","email_address"])
        test_dataframe = obfuscator.get_obfuscated_df()
        assert isinstance(test_dataframe,pd.DataFrame)
        result = obfuscator.get_obfuscated_bytestream(test_dataframe)
        assert isinstance(result, io.BytesIO)

    @pytest.mark.it(
        "When passed with a dataframe, with file_type as csv, and encoding_type as utf-8, returns correct bytestream"
    )
    @mock_aws
    def test_csv_output_utf8_returns_bytestream(self,s3,bucket):
        obfuscator = Obfuscator("s3://test-bucket/new_data/short_test_file.csv",["name","email_address"])
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




#     @pytest.mark.it(
#         "When passed with a dataframe, with file_type as csv, and encoding_type as utf-16, returns correct bytestream"
#     )
#     def test_csv_output_utf16(self, simple_df):
#         result = convert_df_to_bytestream(
#             simple_df, file_type="csv", encoding_type="utf-16"
#         )
#         assert isinstance(result, io.BytesIO)
#         contents = result.getvalue().decode("utf-16")
#         assert "student_id" in contents
#         assert "1234" in contents
#         assert "name" in contents
#         assert "***" in contents
#         assert "course" in contents
#         assert "Software" in contents

    # @pytest.mark.it(
    #     "When passed with a dataframe, with file_type as json, and encoding_type as utf-8, returns correct bytestream"
    # )
    # def test_json_output_utf8_returns_bytestream(self,s3,bucket):
    #     obfuscator = Obfuscator("s3://test-bucket/new_data/short_test_file.json",["name"])
    #     test_dataframe = obfuscator.get_obfuscated_df()
    #     result = obfuscator.get_obfuscated_bytestream(test_dataframe)
    #     assert isinstance(result, io.BytesIO)
    #     contents = result.getvalue().decode("utf-8")
    #     assert "student_id" in contents
    #     assert "1234" in contents
    #     assert "name" in contents
    #     assert "***" in contents
    #     assert "course" in contents
    #     assert "Software" in contents

#     @pytest.mark.it(
#         "When passed with a dataframe, with file_type as json, and encoding_type as utf-8-sig, returns correct bytestream"
#     )
#     def test_json_output_utf8sig(self, simple_df):
#         result = convert_df_to_bytestream(simple_df, file_type="json")
#         assert isinstance(result, io.BytesIO)
#         contents = result.getvalue().decode("utf-8-sig")
#         assert "student_id" in contents
#         assert "1234" in contents
#         assert "name" in contents
#         assert "***" in contents
#         assert "course" in contents
#         assert "Software" in contents

#     @pytest.mark.it(
#         "When passed with a dataframe, with file_type as json, and encoding_type as utf-16, returns correct bytestream"
#     )
#     def test_json_output_utf16(self, simple_df):
#         result = convert_df_to_bytestream(
#             simple_df, file_type="json", encoding_type="utf-16"
#         )
#         assert isinstance(result, io.BytesIO)
#         contents = result.getvalue().decode("utf-16")
#         assert "student_id" in contents
#         assert "1234" in contents
#         assert "name" in contents
#         assert "***" in contents
#         assert "course" in contents
#         assert "Software" in contents

#     @pytest.mark.it(
#         "When passed with a dataframe, with file_type as parquet, returns correct bytestream"
#     )
#     def test_parquet_output(self, simple_df):
#         result = convert_df_to_bytestream(simple_df, file_type="parquet")
#         assert isinstance(result, bytes)
#         assert result.startswith(b"PAR1")
#         assert result.endswith(b"PAR1")


