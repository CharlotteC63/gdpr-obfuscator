import pytest
from src.utils.get_file_key import get_file_key


class TestGetFileKey:

    @pytest.mark.it(
        "When passed with a path in S3 URI format, returns correct key name"
    )
    def test_returns_key_name_from_path_in_S3_URI_format(self):
        test_path = "s3://test-bucket/new_data/file.csv"
        result = get_file_key(test_path)
        assert result == "new_data/file.csv"

    @pytest.mark.it(
        "When passed with a path in HTTTP URL format, virtual-hosted style, returns correct file key"
    )
    def test_returns_key_name_from_path_in_HTTPS_virtual_hosted_format(self):
        test_path = "https://test-bucket.s3.amazonaws.com/new_data/file.csv"
        result = get_file_key(test_path)
        assert result == "new_data/file.csv"

    @pytest.mark.it(
        "When passed with a path in HTTP URL format, path-style, returns correct file key"
    )
    def test_returns_key_name_from_path_in_HTTPS_path_style_format(self):
        test_path = "https://s3.amazonaws.com/test-bucket/new_data/file.csv"
        result = get_file_key(test_path)
        assert result == "new_data/file.csv"

    @pytest.mark.it("When passed with a path in ARN format, returns correct key name")
    def test_returns_key_name_from_path_in_ARN_format(self):
        test_path = "arn:aws:s3:::test-bucket/new_data/file.csv"
        result = get_file_key(test_path)
        assert result == "new_data/file.csv"

    @pytest.mark.it(
        "When passed with a path where the key does not follow the forward slash after bucket name, raises ValueError"
    )
    def test_raise_ValueError_when_key_name_does_not_follow_forward_slash_after_bucket_name_in_path(self):
        test_path = "s3://test-bucket/"
        with pytest.raises(ValueError) as err:
            get_file_key(test_path)
        assert str(err.value) == "Key not found in the file path following bucket name and forward slash"

    @pytest.mark.it(
        "When passed with a path where the key does not follow the bucket name, raises ValueError"
    )
    def test_raise_ValueError_when_key_name_does_not_follow_bucket_name_in_path(self):
        test_path = "s3://test-bucket"
        with pytest.raises(ValueError) as err:
            get_file_key(test_path)
        assert str(err.value) == "Key not found in the file path following bucket name"

    @pytest.mark.it(
        "When passed with a path containing a key name that is over 1024 bytes in UTF-8, violating AWS guidelines, raises ValueError"
    )
    def test_raise_ValueError_when_key_name_exceeds_maximum_bytes(self):
        test_key = "a" * 1025
        test_path = f"s3://test-bucket/{test_key}"
        with pytest.raises(ValueError) as err:
            get_file_key(test_path)
        assert (
            str(err.value)
            == "S3 object key exceeds the maximum length of 1,024 bytes (UTF-8 encoded)"
        )

    @pytest.mark.it(
        "When passed with a path containing an invalid bucket_name, raises ValueError"
    )
    def test_raise_ValueError_when_invalid_bucket_name_passed(self):
        test_path = "s3://Test_Bucket!/new_data/file.csv"
        with pytest.raises(ValueError):
            get_file_key(test_path)
