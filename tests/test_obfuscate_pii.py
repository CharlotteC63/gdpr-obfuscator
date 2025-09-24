import pytest
from src.utils.obfuscate_pii import obfuscate_pii


@pytest.fixture
def simple_file_contents():
    return [
        {
            "student_id": 1234,
            "name": "John Smith",
            "course": "Software",
            "cohort_graduation_date": "2025-03-17",
        }
    ]


@pytest.fixture
def multiple_file_contents():
    return [
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


@pytest.fixture
def file_contents_with_varied_keys():
    return [
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
        },
        {
            "student_id": 2222,
            "name": "Louisa Harthorne",
            "course": "Data Engineering",
            "cohort_graduation_date": "2025-06-23",
            "email_address": "l.harthorne@email.com",
        },
    ]


class TestGetFileKey:

    @pytest.mark.it(
        "When passed with an empty list for file_content, returns an empty list"
    )
    def test_returns_empty_list_when_file_contents_is_empty_list(self):
        file_contents = []
        pii_fields = ["name", "email_address"]
        result = obfuscate_pii(file_contents, pii_fields)
        assert result == []

    @pytest.mark.it(
        "When passed with an empty list for pii_fields, returns file_contents unchanged"
    )
    def test_returns_empty_list_when_pii_fields_is_empty_list(
        self, simple_file_contents
    ):
        pii_fields = []
        result = obfuscate_pii(simple_file_contents, pii_fields)
        assert result == [
            {
                "student_id": 1234,
                "name": "John Smith",
                "course": "Software",
                "cohort_graduation_date": "2025-03-17",
            }
        ]

    @pytest.mark.it(
        """When passed with file_contents that is a list containing one dict, and pii_fields that contains
        a single field name in a list, returns dict of obfuscated data
        """
    )
    def test_returns_list_of_obfuscated_data_for_one_data_point_and_one_pii_field(
        self, simple_file_contents
    ):
        pii_fields = ["name"]
        result = obfuscate_pii(simple_file_contents, pii_fields)
        assert result == [
            {
                "student_id": 1234,
                "name": "***",
                "course": "Software",
                "cohort_graduation_date": "2025-03-17",
            }
        ]

    @pytest.mark.it(
        """When passed with file_contents that is a list containing multiple dicts, and pii_fields that contains
        a single field name in a list, returns dict of obfuscated data
        """
    )
    def test_returns_list_of_obfuscated_data_for_multiple_data_points_and_one_pii_field(
        self, multiple_file_contents
    ):
        pii_fields = ["name"]
        result = obfuscate_pii(multiple_file_contents, pii_fields)
        assert result == [
            {
                "student_id": 1234,
                "name": "***",
                "course": "Software",
                "cohort_graduation_date": "2025-03-17",
            },
            {
                "student_id": 1111,
                "name": "***",
                "course": "Software",
                "cohort_graduation_date": "2025-03-17",
            },
            {
                "student_id": 2222,
                "name": "***",
                "course": "Data Engineering",
                "cohort_graduation_date": "2025-06-23",
            },
        ]

    @pytest.mark.it(
        """When passed with file_contents that is a list containing multiple dicts, and pii_fields that contains
        multiple field names in a list, returns dict of obfuscated data
        """
    )
    def test_returns_list_of_obfuscated_data_for_multiple_data_points_and_multiple_pii_fields(
        self, multiple_file_contents
    ):
        pii_fields = ["name", "course", "cohort_graduation_date"]
        result = obfuscate_pii(multiple_file_contents, pii_fields)
        assert result == [
            {
                "student_id": 1234,
                "name": "***",
                "course": "***",
                "cohort_graduation_date": "***",
            },
            {
                "student_id": 1111,
                "name": "***",
                "course": "***",
                "cohort_graduation_date": "***",
            },
            {
                "student_id": 2222,
                "name": "***",
                "course": "***",
                "cohort_graduation_date": "***",
            },
        ]

    @pytest.mark.it(
        "When passed with a pii field to be obscured that does not appear in every dict, returns correct output"
    )
    def test_returns_list_of_obfuscated_data_when_pii_field_to_be_obscured_does_not_appear_in_every_dict(
        self, file_contents_with_varied_keys
    ):
        pii_fields = ["email_address"]
        result = obfuscate_pii(file_contents_with_varied_keys, pii_fields)
        assert result == [
            {
                "student_id": 1234,
                "name": "John Smith",
                "course": "Software",
                "cohort_graduation_date": "2025-03-17",
                "email_address": "***",
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
                "email_address": "***",
            },
        ]

    @pytest.mark.it(
        "When passed with a pii field not contained in the file_contents, returns file_contents unchanged"
    )
    def test_returns_unchanged_file_contents_when_pii_field_does_not_appear_in_file_contents(
        self, simple_file_contents
    ):
        pii_fields = ["phone_number"]
        result = obfuscate_pii(simple_file_contents, pii_fields)
        assert result == [
            {
                "student_id": 1234,
                "name": "John Smith",
                "course": "Software",
                "cohort_graduation_date": "2025-03-17",
            }
        ]

    @pytest.mark.it(
        "When PII is obfuscated using the function, the input, file_contents, is mutated so that PII is not stored in memory"
    )
    def test_file_contents_input_is_mutated(self, simple_file_contents):
        pii_fields = ["email_address"]
        result = obfuscate_pii(simple_file_contents, pii_fields)
        assert result is simple_file_contents
