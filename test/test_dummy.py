import pytest
from src.dummy_file import dummy

@pytest.mark.it(
        "Dummy test to check CI/CD"
    )
def test_dummy():
    result = dummy()
    assert r