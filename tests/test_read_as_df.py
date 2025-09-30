import pytest
import pandas as pd
import io
from src.utils.read_as_df import read_as_df


class TestReadAsDF:
    @pytest.mark.it("When file is empty, return empty dataframe")
    def test_returns_empty_dataframe_when_file_is_empty(self):
        csv_body = b"\n"
        result = read_as_df(csv_body, "csv")
        assert isinstance(result, pd.DataFrame)

    @pytest.mark.it(
        "When passed with a comma-delimited csv file, returns dataframe with correct contents"
    )
    def test_returns_dataframe_when_passed_with_comma_delimited_csv_file_type(self):
        csv_body = b"student_id,name\n1234,John Smith\n2222,Eliza Andrews\n"
        result = read_as_df(csv_body, "csv")
        assert isinstance(result, pd.DataFrame)
        assert result.iloc[0]["name"] == "John Smith"
        assert result.iloc[1]["name"] == "Eliza Andrews"
        assert result.iloc[0]["student_id"] == 1234
        assert result.iloc[1]["student_id"] == 2222

    @pytest.mark.it(
        "When passed with a semicolon-delimited csv file, returns dataframe with correct contents"
    )
    def test_returns_dataframe_when_passed_with_semicolon_delimited_csv_file(self):
        csv_body = b"student_id;name\n1234;John Smith\n2222;Eliza Andrews\n"
        result = read_as_df(csv_body, "csv")
        assert isinstance(result, pd.DataFrame)
        assert len(result.columns) == 2
        assert len(result.index) == 2
        assert result.iloc[0]["name"] == "John Smith"
        assert result.iloc[1]["name"] == "Eliza Andrews"
        assert result.iloc[0]["student_id"] == 1234
        assert result.iloc[1]["student_id"] == 2222

    @pytest.mark.it(
        "When passed with a tab-delimited csv file, returns dataframe with correct contents"
    )
    def test_returns_dataframe_when_passed_with_tab_delimited_csv_file(self):
        csv_body = b"student_id\tname\n1234\tJohn Smith\n2222\tEliza Andrews\n"
        result = read_as_df(csv_body, "csv")
        assert isinstance(result, pd.DataFrame)
        assert len(result.columns) == 2
        assert len(result.index) == 2
        assert result.iloc[0]["name"] == "John Smith"
        assert result.iloc[1]["name"] == "Eliza Andrews"
        assert result.iloc[0]["student_id"] == 1234
        assert result.iloc[1]["student_id"] == 2222

    @pytest.mark.it(
        "When passed with a json file with a single record, returns dataframe with correct contents"
    )
    def test_returns_dataframe_when_passed_with_json_file_type_single_record(self):
        json_body_format1 = b'{"student_id": 1234, "name": "John Smith"}'
        result = read_as_df(json_body_format1, "json")
        assert isinstance(result, pd.DataFrame)

    @pytest.mark.it(
        "When passed with a json file formatted as an array of records, returns dataframe with correct contents"
    )
    def test_returns_dataframe_when_passed_with_json_file_type_formatted_as_array_of_records(
        self,
    ):
        json_body_format2 = b'[{"student_id": 1234, "name": "John Smith"}, {"student_id": 2222, "name": "Eliza Andrews"}]'
        result = read_as_df(json_body_format2, "json")
        assert isinstance(result, pd.DataFrame)
        assert result.iloc[0]["name"] == "John Smith"
        assert result.iloc[1]["name"] == "Eliza Andrews"
        assert result.iloc[0]["student_id"] == 1234
        assert result.iloc[1]["student_id"] == 2222

    @pytest.mark.it(
        "When passed with a json file formatted as a nested array of records, returns dataframe with correct contents"
    )
    def test_returns_dataframe_when_passed_with_json_file_type_formatted_as_nested_array_of_records(
        self,
    ):
        json_body_format3 = b'{"students": [{"student_id": 1234, "name": "John Smith"}, {"student_id": 2222, "name": "Eliza Andrews"}]}'
        result = read_as_df(json_body_format3, "json")
        assert isinstance(result, pd.DataFrame)
        assert result.iloc[0]["name"] == "John Smith"
        assert result.iloc[1]["name"] == "Eliza Andrews"
        assert result.iloc[0]["student_id"] == 1234
        assert result.iloc[1]["student_id"] == 2222

    @pytest.mark.it("When passed with a parquet file, returns dataframe")
    def test_returns_dataframe_when_passed_with_parquet_file_type(self):
        test_df = pd.DataFrame(
            {"student_id": [1234, 2222], "name": ["John Smith", "Eliza Andrews"]}
        )
        parquet_bytes = io.BytesIO()
        test_df.to_parquet(parquet_bytes, engine="pyarrow")
        parquet_bytes.seek(0)
        result = read_as_df(parquet_bytes.getvalue(), "parquet")
        assert isinstance(result, pd.DataFrame)
        assert result.equals(test_df)

    @pytest.mark.it(
        "Raises ValueError with appropriate message when passed with an unsupported file type"
    )
    def test_raises_value_error_when_passed_with_unsupported_file_type(self):
        txt_body = b"name\nJohn Smith\nstudent_id\n1234\n"
        with pytest.raises(ValueError) as err:
            read_as_df(txt_body, "txt")
        assert (
            str(err.value) == "Unsupported file type: txt, must be csv, json or parquet"
        )

    @pytest.mark.it("When file is encoded using utf-16, returns correct dataframe")
    def test_returns_correct_dataframe_with_utf16_encoding(self):
        csv_body = b"student_id,name\n1234,John Smith\n2222,Eliza Andrews\n"
        result = read_as_df(csv_body, "csv", "utf-16")
        assert isinstance(result, pd.DataFrame)
        assert result.iloc[0]["name"] == "John Smith"
        assert result.iloc[1]["name"] == "Eliza Andrews"
        assert result.iloc[0]["student_id"] == 1234
        assert result.iloc[1]["student_id"] == 2222

    @pytest.mark.it("When file is encoded using utf-8-sig, returns correct dataframe")
    def test_returns_correct_dataframe_with_utf8sig_encoding(self):
        csv_body = b"student_id,name\n1234,John Smith\n2222,Eliza Andrews\n"
        result = read_as_df(csv_body, "csv", "utf-8-sig")
        assert isinstance(result, pd.DataFrame)
        assert result.iloc[0]["name"] == "John Smith"
        assert result.iloc[1]["name"] == "Eliza Andrews"
        assert result.iloc[0]["student_id"] == 1234
        assert result.iloc[1]["student_id"] == 2222
