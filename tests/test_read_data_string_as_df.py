import pytest
import pandas as pd
from src.utils.read_data_string_as_df import read_data_string_as_df


class TestReadcsvasdf:

    @pytest.mark.it("When passed with an empty string, returns None")
    def test_returns_empty_list_when_file_contents_is_empty_list(self):
        csv_string = ""
        result = read_data_string_as_df(csv_string)
        assert result is None

    @pytest.mark.it(
        "When passed with a simple, non-empty, csv string, returns pandas dataframe"
    )
    def test_returns_dataframe_for_non_empty_csv_string(self):
        csv_string = 'name\n"John Smith"'
        result = read_data_string_as_df(csv_string)
        assert isinstance(result, pd.DataFrame)

    @pytest.mark.it(
        "When passed with a simple, non-empty, csv string, returns pandas dataframe containing correct data"
    )
    def test_returns_dataframe_for_non_empty_csv_string_with_correct_contents(self):
        csv_string = 'name\n"John Smith"'
        result = read_data_string_as_df(csv_string)
        assert result.iloc[0]["name"] == "John Smith"

    @pytest.mark.it(
        """
        When passed with a csv string that contains single quotation marks, returns pandas dataframe
        containing correct data
    """
    )
    def test_returns_correct_dataframe_when_csv_string_contains_single_quotation_marks(
        self,
    ):
        csv_string = "name\n'John Smith'"
        result = read_data_string_as_df(csv_string)
        assert result.iloc[0]["name"] == "John Smith"

    @pytest.mark.it(
        "When passed with a csv string that is semicolon delimited, returns pandas dataframe"
    )
    def test_returns_correct_dataframe_when_csv_string_is_semicolon_delimited(
        self,
    ):
        csv_string = 'name;course\n"John Smith";"Software"'
        result = read_data_string_as_df(csv_string)
        assert result.iloc[0]["name"] == "John Smith"
        assert result.iloc[0]["course"] == "Software"

    @pytest.mark.it(
        """
        When passed with a csv string that is semicolon delimited and contains
        single quotes, returns pandas dataframe
    """
    )
    def test_returns_correct_dataframe_when_csv_string_is_semicolon_delimited_and_contains_single_quotes(
        self,
    ):
        csv_string = "name;course\n'John Smith';'Software'"
        result = read_data_string_as_df(csv_string)
        assert result.iloc[0]["name"] == "John Smith"
        assert result.iloc[0]["course"] == "Software"
