import pytest
from src.utils.get_file_name_and_type_from_key import get_file_name_and_type_from_key


class TestGetFileNameAndTypeFromKey:

    @pytest.mark.it(
        "When passed with key for a csv file in the root of an s3 bucket, returns correct file name"
    )
    def test_returns_correct_file_name_for_simplest_path_to_csv(self):
        test_path = "file.csv"
        result = get_file_name_and_type_from_key(test_path)
        assert result["name"] == "file.csv"

    @pytest.mark.it(
        "When passed with key for a csv file in the root of an s3 bucket, returns correct file type"
    )
    def test_returns_correct_file_type_for_simplest_path_to_csv(self):
        test_path = "file.csv"
        result = get_file_name_and_type_from_key(test_path)
        assert result["file_type"] == "csv"

    @pytest.mark.it(
        "When passed with key for a json file in the root of an s3 bucket, returns correct file name"
    )
    def test_returns_correct_file_name_for_simplest_path_to_json(self):
        test_path = "file.json"
        result = get_file_name_and_type_from_key(test_path)
        assert result["name"] == "file.json"

    @pytest.mark.it(
        "When passed with key for a json file in the root of an s3 bucket, returns correct file name"
    )
    def test_returns_correct_file_type_for_simplest_path_to_json(self):
        test_path = "file.json"
        result = get_file_name_and_type_from_key(test_path)
        assert result["file_type"] == "json"

    @pytest.mark.it(
        "When passed with key for a parquet file in the root of an s3 bucket, returns correct file name"
    )
    def test_returns_correct_file_name_for_simplest_path_to_parquet(self):
        test_path = "file.parquet"
        result = get_file_name_and_type_from_key(test_path)
        assert result["name"] == "file.parquet"

    @pytest.mark.it(
        "When passed with key for a parquet file in the root of an s3 bucket, returns correct file name"
    )
    def test_returns_correct_file_type_for_simplest_path_to_parquet(self):
        test_path = "file.parquet"
        result = get_file_name_and_type_from_key(test_path)
        assert result["file_type"] == "parquet"

    @pytest.mark.it(
        "When passed with key containing multiple periods, returns correct file name and key"
    )
    def test_returns_correct_file_name_and_type_when_file_name_contains_multiple_periods(
        self,
    ):
        test_path = "f.i.l.e.csv"
        result = get_file_name_and_type_from_key(test_path)
        assert result["name"] == "f.i.l.e.csv"
        assert result["file_type"] == "csv"

    @pytest.mark.it(
        "When file is saved in subfolder of s3, returns correct file name and type"
    )
    def test_returns_correct_file_name_and_type_when_file_saved_in_subfolder_of_s3(
        self,
    ):
        test_path = "folder/file.csv"
        result = get_file_name_and_type_from_key(test_path)
        assert result["name"] == "file.csv"
        assert result["file_type"] == "csv"

    @pytest.mark.it(
        "When file is saved in multiple subfolders of s3, returns correct file name and type"
    )
    def test_returns_correct_file_name_and_type_when_file_saved_in_multiple_subfolders_of_s3(
        self,
    ):
        test_path = "folder1/folder2/folder3/folder4/file.csv"
        result = get_file_name_and_type_from_key(test_path)
        assert result["name"] == "file.csv"
        assert result["file_type"] == "csv"

    @pytest.mark.it(
        "Raise ValueError with appropriate message for unsupported file type"
    )
    def test_raises_ValueError_when_key_contains_unsupported_file_path(self):
        test_path = "file.txt"
        with pytest.raises(ValueError) as err:
            get_file_name_and_type_from_key(test_path)
        assert (
            str(err.value) == "file_type not supported (must be csv, json or parquet)"
        )
