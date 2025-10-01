import pytest
import pandas as pd
import io
from src.utils.convert_df_to_bytestream import convert_df_to_bytestream


@pytest.fixture
def simple_df():
    data = {
        "student_id": 1234,
        "name": "***",
        "course": "Software",
    }
    return pd.DataFrame([data])


class TestConvertDFToBytestream:

    @pytest.mark.it(
        "Raises TypeError with appropriate message when passed with any object other than a dataframe"
    )
    def test_raises_TypeError_when_passed_with_object_that_is_not_dataframe(self):
        with pytest.raises(TypeError) as err:
            convert_df_to_bytestream([], "csv")
        assert str(err.value) == "Expected dataframe but received <class 'list'>"

    @pytest.mark.it(
        "Raises ValueError with appropriate message when passed with empty string as file_type"
    )
    def test_empty_file_type(self, simple_df):
        with pytest.raises(ValueError) as err:
            convert_df_to_bytestream(simple_df, "")
        assert str(err.value) == "File type cannot be empty"

    @pytest.mark.it(
        "Raises ValueError with appropriate message when passed with an unsupported file_type"
    )
    def test_unsupported_file_type(self, simple_df):
        with pytest.raises(ValueError) as err:
            convert_df_to_bytestream(simple_df, "txt")
        assert (
            str(err.value)
            == "File type, txt, is not supported, must be csv, json or parquet"
        )

    @pytest.mark.it(
        "When passed with a dataframe, with file_type as csv, and encoding_type as utf-8, returns correct bytestream"
    )
    def test_csv_output_utf8(self, simple_df):
        result = convert_df_to_bytestream(simple_df, file_type="csv")
        assert isinstance(result, io.BytesIO)
        contents = result.getvalue().decode("utf-8")
        assert "student_id" in contents
        assert "1234" in contents
        assert "name" in contents
        assert "***" in contents
        assert "course" in contents
        assert "Software" in contents

    @pytest.mark.it(
        "When passed with a dataframe, with file_type as csv, and encoding_type as utf-8-sig, returns correct bytestream"
    )
    def test_csv_output_utf8sig(self, simple_df):
        result = convert_df_to_bytestream(
            simple_df, file_type="csv", encoding_type="utf-8-sig"
        )
        assert isinstance(result, io.BytesIO)
        contents = result.getvalue().decode("utf-8-sig")
        assert "student_id" in contents
        assert "1234" in contents
        assert "name" in contents
        assert "***" in contents
        assert "course" in contents
        assert "Software" in contents

    @pytest.mark.it(
        "When passed with a dataframe, with file_type as csv, and encoding_type as utf-16, returns correct bytestream"
    )
    def test_csv_output_utf16(self, simple_df):
        result = convert_df_to_bytestream(
            simple_df, file_type="csv", encoding_type="utf-16"
        )
        assert isinstance(result, io.BytesIO)
        contents = result.getvalue().decode("utf-16")
        assert "student_id" in contents
        assert "1234" in contents
        assert "name" in contents
        assert "***" in contents
        assert "course" in contents
        assert "Software" in contents

    @pytest.mark.it(
        "When passed with a dataframe, with file_type as json, and encoding_type as utf-8, returns correct bytestream"
    )
    def test_json_output_utf8(self, simple_df):
        result = convert_df_to_bytestream(simple_df, file_type="json")
        assert isinstance(result, io.BytesIO)
        contents = result.getvalue().decode("utf-8")
        assert "student_id" in contents
        assert "1234" in contents
        assert "name" in contents
        assert "***" in contents
        assert "course" in contents
        assert "Software" in contents

    @pytest.mark.it(
        "When passed with a dataframe, with file_type as json, and encoding_type as utf-8-sig, returns correct bytestream"
    )
    def test_json_output_utf8sig(self, simple_df):
        result = convert_df_to_bytestream(simple_df, file_type="json")
        assert isinstance(result, io.BytesIO)
        contents = result.getvalue().decode("utf-8-sig")
        assert "student_id" in contents
        assert "1234" in contents
        assert "name" in contents
        assert "***" in contents
        assert "course" in contents
        assert "Software" in contents

    @pytest.mark.it(
        "When passed with a dataframe, with file_type as json, and encoding_type as utf-16, returns correct bytestream"
    )
    def test_json_output_utf16(self, simple_df):
        result = convert_df_to_bytestream(
            simple_df, file_type="json", encoding_type="utf-16"
        )
        assert isinstance(result, io.BytesIO)
        contents = result.getvalue().decode("utf-16")
        assert "student_id" in contents
        assert "1234" in contents
        assert "name" in contents
        assert "***" in contents
        assert "course" in contents
        assert "Software" in contents

    @pytest.mark.it(
        "When passed with a dataframe, with file_type as parquet, returns correct bytestream"
    )
    def test_parquet_output(self, simple_df):
        result = convert_df_to_bytestream(simple_df, file_type="parquet")
        assert isinstance(result, bytes)
        assert result.startswith(b"PAR1")
        assert result.endswith(b"PAR1")
