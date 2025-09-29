import pytest
import pandas as pd
from src.utils.obfuscate_pii import obfuscate_pii


@pytest.fixture
def simple_df():
    data = {
        "student_id": 1234,
        "name": "John Smith",
        "course": "Software",
        "cohort_graduation_date": "2025-03-17",
    }
    return pd.DataFrame([data])


@pytest.fixture
def multiple_row_df():
    data = [
        {
            "student_id": 1234,
            "name": "John Smith",
            "course": "Software",
            "cohort_graduation_date": "2025-03-17",
        },
        {
            "student_id": 1111,
            "name": "Amy Carol",
            "course": "Software",
            "cohort_graduation_date": "2025-03-17",
        },
        {
            "student_id": 2222,
            "name": "Louisa Harthorne",
            "course": "Data Engineering",
            "cohort_graduation_date": "2025-06-23",
        },
    ]
    return pd.DataFrame(data)


@pytest.fixture
def varied_columns_dataframe():
    data = [
        {
            "student_id": 1234,
            "name": "John Smith",
            "course": "Software",
            "cohort_graduation_date": "2025-03-17",
            "email_address": "j.smith@email.com",
        },
        {
            "student_id": 1111,
            "name": "Amy Carol",
            "course": "Software",
            "cohort_graduation_date": "2025-03-17",
            "email_address": "",
        },
        {
            "student_id": 2222,
            "name": "",
            "course": "Data Engineering",
            "cohort_graduation_date": "2025-06-23",
            "email_address": "l.harthorne@email.com",
        },
    ]
    return pd.DataFrame(data)


class TestObfuscatePII:

    @pytest.mark.it("When passed with a dataframe, returns a dataframe")
    def test_returns_dataframe_when_passed_with_dataframe(self, simple_df):
        result = obfuscate_pii(simple_df, ["name"])
        assert isinstance(result, pd.DataFrame)

    @pytest.mark.it("When passed with an empty dataframe, returns an empty dataframe")
    def test_returns_empty_dataframe_when_passed_with_empty_dataframe(self, simple_df):
        empty_df = pd.DataFrame()
        result = obfuscate_pii(empty_df, ["name"])
        assert result is empty_df

    @pytest.mark.it(
        """When passed with a dataframe, returns a mutated version of the dataframe, as opposed to a new dataframe, for
        security reasons (so that PII is not saved in memory)"""
    )
    def test_returns_mutated_dataframe(self, simple_df):
        result = obfuscate_pii(simple_df, ["name"])
        assert result is simple_df

    @pytest.mark.it(
        "When passed with a dataframe and pii_fields is an empty list, returns same dataframe"
    )
    def test_returns_same_dataframe_when_pii_fields_is_empty_list(self, simple_df):
        result = obfuscate_pii(simple_df, [])
        assert result is simple_df

    @pytest.mark.it(
        "When passed with a dataframe that doesn't contain column headings matching pii_fields, returns same dataframe"
    )
    def test_returns_same_dataframe_when_pii_fields_not_in_dataframe(self, simple_df):
        result = obfuscate_pii(simple_df, ["phone number"])
        assert result is simple_df

    @pytest.mark.it(
        """When passed with a one-row dataframe that contains one pii_field, returns a dataframe with the same data but
        with that one column obscufated"""
    )
    def test_returns_one_row_dataframe_with_one_pii_field_obfuscated(self, simple_df):
        result = obfuscate_pii(simple_df, ["name"])
        assert len(result.index) == 1
        assert len(result.columns) == 4
        assert isinstance(result, pd.DataFrame)
        assert result.iloc[0]["name"] == "***"
        assert result.iloc[0]["cohort_graduation_date"] == "2025-03-17"
        assert result.iloc[0]["student_id"] == 1234
        assert result.iloc[0]["course"] == "Software"

    @pytest.mark.it(
        """When passed with a one-row dataframe that contains two pii_fields, returns a dataframe with the same data
        but with those two pii columns obscufated"""
    )
    def test_returns_one_row_dataframe_with_two_pii_fields_obfuscated_and_rest_unchanged(
        self, simple_df
    ):
        result = obfuscate_pii(simple_df, ["name", "cohort_graduation_date"])
        assert isinstance(result, pd.DataFrame)
        assert len(result.index) == 1
        assert len(result.columns) == 4
        assert result.iloc[0]["name"] == "***"
        assert result.iloc[0]["cohort_graduation_date"] == "***"
        assert result.iloc[0]["student_id"] == 1234
        assert result.iloc[0]["course"] == "Software"

    @pytest.mark.it(
        """When passed with a multiple-row dataframe that contains one pii_field, returns a dataframe with the same
        data, but with that pii column obfuscated"""
    )
    def test_returns_multiple_row_dataframe_with_one_pii_field_obfuscated_and_rest_unchanged(
        self, multiple_row_df
    ):
        result = obfuscate_pii(multiple_row_df, ["name"])
        assert isinstance(result, pd.DataFrame)
        assert len(result.index) == 3
        assert len(result.columns) == 4
        assert result.iloc[0]["name"] == "***"
        assert result.iloc[1]["name"] == "***"
        assert result.iloc[2]["name"] == "***"

    @pytest.mark.it(
        "When passed with a multiple-row dataframe that contains only one of the two pii_fields, returns same dataframe with that column obscufated"
    )
    def test_returns_multiple_row_dataframe_with_one_pii_field_obfuscated(
        self, multiple_row_df
    ):
        result = obfuscate_pii(multiple_row_df, ["course", "phone number"])
        assert isinstance(result, pd.DataFrame)
        assert len(result.index) == 3
        assert len(result.columns) == 4
        assert result.iloc[0]["course"] == "***"
        assert result.iloc[1]["course"] == "***"
        assert result.iloc[2]["course"] == "***"
        assert "phone number" not in result.columns

    @pytest.mark.it(
        "When passed with a dataframe that contains empty rows or missing data, returns pii obfuscated"
    )
    def test_returns_correct_data_obfuscated_when_dataframe_has_empty_rows(
        self, varied_columns_dataframe
    ):
        result = obfuscate_pii(varied_columns_dataframe, ["name", "email_address"])
        assert isinstance(result, pd.DataFrame)
        assert len(result.index) == 3
        assert len(result.columns) == 5
        assert result.iloc[0]["name"] == "***"
        assert result.iloc[1]["name"] == "***"
        assert result.iloc[2]["name"] == "***"
        assert result.iloc[0]["email_address"] == "***"
        assert result.iloc[1]["email_address"] == "***"
        assert result.iloc[2]["email_address"] == "***"
