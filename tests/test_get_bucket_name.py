import pytest
from src.utils.get_bucket_name import get_bucket_name


class TestGetBucketName:

    @pytest.mark.it(
        "When passed with a path in S3 URI format, returns correct bucket name"
    )
    def test_returns_bucket_name_from_path_in_S3_URI_format(self):
        test_path = "s3://test-bucket/new_data/file.csv"
        result = get_bucket_name(test_path)
        assert result == "test-bucket"

    @pytest.mark.it(
        "When passed with a path in HTTTP URL format, virtual-hosted style, returns correct bucket name"
    )
    def test_returns_bucket_name_from_path_in_HTTPS_virtual_hosted_format(self):
        test_path = "https://test-bucket.s3.amazonaws.com/new_data/file.csv"
        result = get_bucket_name(test_path)
        assert result == "test-bucket"

    @pytest.mark.it(
        "When passed with a path in HTTP URL format, path-style, returns correct bucket name"
    )
    def test_returns_bucket_name_from_path_in_HTTPS_path_style_format(self):
        test_path = "https://s3.amazonaws.com/test-bucket/new_data/file.csv"
        result = get_bucket_name(test_path)
        assert result == "test-bucket"

    @pytest.mark.it(
        "When passed with a path in ARN format, returns correct bucket name"
    )
    def test_returns_bucket_name_from_path_in_ARN_format(self):
        test_path = "arn:aws:s3:::test-bucket/new_data/file.csv"
        result = get_bucket_name(test_path)
        assert result == "test-bucket"

    @pytest.mark.it("When passed with a non-string type, raises TypeError")
    def test_raise_exception_when_passed_with_type_other_than_string(self):
        with pytest.raises(TypeError) as err1:
            get_bucket_name(["https://s3.amazonaws.com/test-bucket/new_data/file.csv"])
        assert str(err1.value) == "Path to file must be a string"
        with pytest.raises(TypeError) as err1:
            get_bucket_name(
                {"path": "https://s3.amazonaws.com/test-bucket/new_data/file.csv"}
            )
        assert str(err1.value) == "Path to file must be a string"

    @pytest.mark.it("When passed with empty string, raises ValueError")
    def test_raise_exception_when_passed_with_empty_string(self):
        with pytest.raises(ValueError) as err:
            get_bucket_name("")
        assert str(err.value) == "Invalid path provided"

    @pytest.mark.it("When passed with a path of invalid format, raises ValueError")
    def test_raise_ValueError_when_invalid_path_format_provided(self):
        with pytest.raises(ValueError) as err1:
            get_bucket_name("test-bucket/new_data/file.csv")
        assert str(err1.value) == "Invalid path provided"
        with pytest.raises(ValueError) as err2:
            get_bucket_name("new_data/file.csv")
        assert str(err2.value) == "Invalid path provided"

    @pytest.mark.it(
        "When passed with path containing bucket name that violates AWS naming guidelines, raises ValueError"
    )
    def test_raise_ValueError_when_bucket_name_violates_guidelines(self):
        # violation: contains underscore
        with pytest.raises(ValueError) as err1:
            get_bucket_name("test_bucket/new_data/file.csv")
        assert str(err1.value) == "Invalid path provided"
        # violation: contains special character !
        with pytest.raises(ValueError) as err2:
            get_bucket_name("test!bucket/new_data/file.csv")
        assert str(err2.value) == "Invalid path provided"
        # violation: contains special character @
        with pytest.raises(ValueError) as err3:
            get_bucket_name("@testbucket/new_data/file.csv")
        assert str(err3.value) == "Invalid path provided"
        # violation: contains fewer than 3 characters
        with pytest.raises(ValueError) as err4:
            get_bucket_name("tb/new_data/file.csv")
        assert str(err4.value) == "Invalid path provided"
        # violation: contains more than 63 characters
        with pytest.raises(ValueError) as err5:
            get_bucket_name(
                "testbuckettttttttttttttttttttttttttttttttttttttttttttttttttttttt/new_data/file.csv"
            )
        assert str(err5.value) == "Invalid path provided"
        # violation: contains uppercase character
        with pytest.raises(ValueError) as err6:
            get_bucket_name("TestBucket/new_data/file.csv")
        assert str(err6.value) == "Invalid path provided"
