import pytest
import boto3
import os
from moto import mock_aws
from src.lambda_function import lambda_handler


@pytest.fixture(scope="function")
def aws_creds():
    # Mocked aws credentials for moto
    os.environ["AWS_ACCESS_KEY_ID"] = "Test"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "Test"
    os.environ["AWS_SESSION_TOKEN"] = "Test"
    os.environ["AWS_SECURITY_TOKEN"] = "Test"
    os.environ["AWS_DEFAULT_REGION"] = "eu-north-1"


class TestLambdaHandler:

    @pytest.mark.it(
        "When passed with a valid event, the lambda function returns a 200 status code and success message"
    )
    @mock_aws
    def test_lambda_function_returns_200_status_code_and_success_message_when_invoked_correctly(
        self, aws_creds
    ):
        s3_client = boto3.client("s3")
        s3_client.create_bucket(
            Bucket="test-bucket",
            CreateBucketConfiguration={"LocationConstraint": "eu-north-1"},
        )
        with open("tests/data/dummy_data_long.csv", "rb") as file:
            s3_client.put_object(
                Body=file, Bucket="test-bucket", Key="new_data/long_test_file.csv"
            )
        event = {
            "file_to_obfuscate": "s3://test-bucket/new_data/long_test_file.csv",
            "pii_fields": ["name", "email_address"],
        }
        result = lambda_handler(event, {})
        assert result == {
            "statusCode": 200,
            "body": "Obfuscated file successfully uploaded to s3://test-bucket/obfuscated_data/long_test_file.csv",
        }

    @pytest.mark.it(
        """When passed with an invalid event, the lambda function returns a 400 status code and correct error message,
        when the error is a custom module error"""
    )
    @mock_aws
    def test_lambda_function_returns_400_status_code_and_correct_custom_error_message_when_invoked_incorrectly(
        self, aws_creds
    ):
        s3_client = boto3.client("s3")
        s3_client.create_bucket(
            Bucket="test-bucket",
            CreateBucketConfiguration={"LocationConstraint": "eu-north-1"},
        )
        event = {
            "file_to_obfuscate": "s3://invalid_bucket_name/new_data/long_test_file.csv",
            "pii_fields": ["name", "email_address"],
        }
        result = lambda_handler(event, {})
        assert result == {
            "statusCode": 400,
            "body": (
                "Failed to obfuscate file: Invalid bucket name according to AWS rules, "
                "see https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucketnamingrules.html"
            ),
        }

    @pytest.mark.it(
        """When passed with an invalid event, the lambda function returns a 400 status code and correct error message,
        when the error is a ClientError"""
    )
    @mock_aws
    def test_lambda_function_returns_400_status_code_and_short_ClientError_message_when_invoked_incorrectly(
        self, aws_creds
    ):
        s3_client = boto3.client("s3")
        s3_client.create_bucket(
            Bucket="test-bucket",
            CreateBucketConfiguration={"LocationConstraint": "eu-north-1"},
        )
        event = {
            "file_to_obfuscate": "s3://nonexistent-bucket/new_data/long_test_file.csv",
            "pii_fields": ["name", "email_address"],
        }
        result = lambda_handler(event, {})
        assert result == {
            "statusCode": 400,
            "body": "Failed to obfuscate file: The specified bucket does not exist",
        }
