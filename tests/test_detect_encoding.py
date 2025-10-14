import pytest
from src.utils.detect_encoding import detect_encoding


@pytest.fixture
def sample_text():
    return "test sample text"


class TestDecode:

    @pytest.mark.it(
        "when raw_btyes are utf-8 encoded, returns string of correct encoding type"
    )
    def test_decoding_utf_8(self, sample_text):
        utf8_bytes = sample_text.encode("utf-8")
        result = detect_encoding(utf8_bytes)
        assert result == "utf-8"

    @pytest.mark.it(
        "when raw_btyes are utf-16 encoded, returns string of correct encoding type"
    )
    def test_decoding_utf_16(self, sample_text):
        utf16_bytes = sample_text.encode("utf-16")
        result = detect_encoding(utf16_bytes)
        assert result == "utf-16"

    @pytest.mark.it(
        "when raw_btyes are utf-8-sig encoded, returns string of correct encoding type"
    )
    def test_decoding_utf_8_sig(self, sample_text):
        utf8sig_bytes = sample_text.encode("utf-8-sig")
        result = detect_encoding(utf8sig_bytes)
        assert result == "utf-8-sig"

    @pytest.mark.it("when passed with an object that is not bytes, raises error")
    def test_decoding_unsupported(self, sample_text):
        unsupported_encoding_bytes = "Unsupported"
        with pytest.raises(ValueError) as err:
            detect_encoding(unsupported_encoding_bytes)
        assert (
            str(err.value)
            == "Could not decode using utf-8, utf-8-sig or utf-16, check file encoding"
        )
