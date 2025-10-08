import os
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
        "Returns correct dataframe for short csv file with one column of pii"
    )
    def test_returns_correct_dataframe_for_short_csv_file_with_one_column_of_pii(self,s3,bucket):
        obfuscator = Obfuscator('s3://test-bucket/new_data/short_test_file.csv',['name'])
        obfuscated_df = obfuscator.get_obfuscated_df()
        assert len(obfuscated_df.index) == 1
        assert len(obfuscated_df.columns) == 5
        assert isinstance(obfuscated_df, pd.DataFrame)
        assert obfuscated_df.iloc[0]["name"] == "***"
        assert obfuscated_df.iloc[0]["cohort_graduation_date"] == "2025-03-17"
        assert obfuscated_df.iloc[0]["student_id"] == 1234
        assert obfuscated_df.iloc[0]["course"] == "Software"
