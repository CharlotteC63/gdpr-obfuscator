import pytest
import pandas as pd
from src.utils.read_data_string_as_df import read_data_string_as_df


class TestReadcsvasdf:

    @pytest.mark.it("When passed with an empty string, returns None")
    def test_returns_empty_list_when_file_contents_is_empty_list(self):
        csv_string = ""
        result = read_data_string_as_df(csv_string, "csv")
        assert result is None

    @pytest.mark.it(
        "When passed with a simple, non-empty, csv string, returns pandas dataframe"
    )
    def test_returns_dataframe_for_non_empty_csv_string(self):
        csv_string = 'name\n"John Smith"'
        result = read_data_string_as_df(csv_string, "csv")
        assert isinstance(result, pd.DataFrame)

    @pytest.mark.it(
        "When passed with a simple, non-empty, csv string, returns pandas dataframe containing correct data"
    )
    def test_returns_dataframe_for_non_empty_csv_string_with_correct_contents(self):
        csv_string = 'name\n"John Smith"'
        result = read_data_string_as_df(csv_string, "csv")
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
        result = read_data_string_as_df(csv_string, "csv")
        assert result.iloc[0]["name"] == "John Smith"

    @pytest.mark.it(
        "When passed with a csv string that is semicolon delimited, returns pandas dataframe"
    )
    def test_returns_correct_dataframe_when_csv_string_is_semicolon_delimited(
        self,
    ):
        csv_string = 'name;course\n"John Smith";"Software"'
        result = read_data_string_as_df(csv_string, "csv")
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
        result = read_data_string_as_df(csv_string, "csv")
        assert result.iloc[0]["name"] == "John Smith"
        assert result.iloc[0]["course"] == "Software"

    @pytest.mark.it(
        "When passed with a simple common format json string, returns pandas dataframe"
    )
    def test_returns_dataframe_when_passed_with_json_string(
        self,
    ):
        json_string = '{"records":[{"name": "John Smith"}]}'
        result = read_data_string_as_df(json_string, "json")
        assert isinstance(result, pd.DataFrame)

    @pytest.mark.it(
        "When passed with a simple common format json string, returns pandas dataframe containing correct data"
    )
    def test_returns_dataframe_containing_correct_data_when_passed_with_simple_json_string_common_format(
        self,
    ):
        json_string = '{"records":[{"name": "John Smith"}]}'
        result = read_data_string_as_df(json_string, "json")
        assert len(result.columns) == 1
        assert len(result.index) == 1
        assert result.iloc[0]["name"] == "John Smith"

    @pytest.mark.it(
        "When passed with a longer common format json string, returns pandas dataframe containing correct data"
    )
    def test_returns_dataframe_containing_correct_data_when_passed_with_long_json_string_common_format(
        self,
    ):
        json_string = """{"records":[{"student_id": 1234,"name": "John Smith","course": "Software"},
                                    {"student_id": 2222,"name": "Lily Allen","course": "DevOps"},
                                    {"student_id": 3333,"name": "Paul Richmond","course": "Software"}]}"""
        result = read_data_string_as_df(json_string, "json")
        assert len(result.columns) == 3
        assert len(result.index) == 3
        assert result.iloc[0]["name"] == "John Smith"

    @pytest.mark.it(
        "When passed with a simple flat list format json string, returns pandas dataframe containing correct data"
    )
    def test_returns_dataframe_containing_correct_data_when_passed_with_simple_json_string_flat_list_format(
        self,
    ):
        json_string = '[{"name": "John Smith"}]'
        result = read_data_string_as_df(json_string, "json")
        assert len(result.columns) == 1
        assert len(result.index) == 1
        assert result.iloc[0]["name"] == "John Smith"

    @pytest.mark.it(
        "When passed with a longer flat list format json string, returns pandas dataframe containing correct data"
    )
    def test_returns_dataframe_containing_correct_data_when_passed_with_long_json_string_flat_list_format(
        self,
    ):
        json_string = """[{"student_id": 1234,"name": "John Smith","course": "Software"},
                        {"student_id": 2222,"name": "Lily Allen","course": "DevOps"},
                        {"student_id": 3333,"name": "Paul Richmond","course": "Software"}]"""
        result = read_data_string_as_df(json_string, "json")
        assert len(result.columns) == 3
        assert len(result.index) == 3
        assert result.iloc[0]["name"] == "John Smith"

    @pytest.mark.it(
        "When passed with a simple nested dictionary format json string, returns pandas dataframe containing correct data"
    )
    def test_returns_dataframe_containing_correct_data_when_passed_with_simple_json_string_nested_dict_format(
        self,
    ):
        json_string = '{"records": {"name": "John Smith"}}'
        result = read_data_string_as_df(json_string, "json")
        assert len(result.columns) == 1
        assert len(result.index) == 1
        assert result.iloc[0]["name"] == "John Smith"

    @pytest.mark.it("Raise ValueError when passed with unsupported json format")
    def test_raises_ValueError_when_passed_with_unsupported_json_format(
        self,
    ):
        json_string = "invalid_format"
        with pytest.raises(ValueError) as err:
            read_data_string_as_df(json_string, "json")
        assert str(err.value) == "Unsupported json structure"
