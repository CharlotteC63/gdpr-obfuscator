import pytest
import pandas as pd
from src.utils.df_to_string import df_to_string


class TestDFtoString:

    @pytest.mark.it(
        "When passed with an empty dataframe, returns an empty string, regardless of file type"
    )
    def test_when_passed_with_empty_df_returns_empty_string(self):
        empty_df = pd.DataFrame()
        assert df_to_string(empty_df, "csv") == ""
        assert df_to_string(empty_df, "json") == ""
        assert df_to_string(empty_df, "parquet") == ""

    @pytest.mark.it(
        "When passed with a simple one-row one-column dataframe, and csv filetype, returns data as csv string"
    )
    def test_when_passed_simple_dataframe_and_csv_original_filetype_returns_data_as_csv_string(
        self,
    ):
        data = {"name": "***"}
        simple_df = pd.DataFrame([data])
        assert df_to_string(simple_df, "csv") == "name\n***\n"

    @pytest.mark.it(
        "When passed with a simple one-row one-column dataframe, and json filetype, returns data as json string"
    )
    def test_when_passed_simple_dataframe_and_json_original_filetype_returns_data_as_json_string(
        self,
    ):
        data = {"name": "***"}
        simple_df = pd.DataFrame([data])
        assert df_to_string(simple_df, "json") == "{'records':[{'name': '***'}]}"

    @pytest.mark.it(
        "When passed with a simple one-row one-column dataframe, and parquet filetype, returns data as parquet string"
    )
    def test_when_passed_simple_dataframe_and_parquet_original_filetype_returns_data_as_parquet_string(
        self,
    ):
        data = {"name": "***"}
        simple_df = pd.DataFrame([data])
        result = df_to_string(simple_df, "parquet")
        assert isinstance(result, bytes)

    @pytest.mark.it(
        "Raises ValueError when passed with a filetype that is not csv, json or parquet"
    )
    def test_raise_ValueError_when_passed_with_unsupported_filetype(self):
        data = {"name": "***"}
        simple_df = pd.DataFrame([data])
        with pytest.raises(ValueError) as err:
            df_to_string(simple_df, "txt")
        assert (
            str(err.value) == "file_type not supported (must be csv, json or parquet)"
        )
