import pytest
from src.utils.decode import decode


@pytest.fixture
def sample_text():
    return "test sample text"


class TestDecode:

    @pytest.mark.it("when raw_btyes are utf-8 encoded, returns decoded output")
    def test_decoding_utf_8(self, sample_text):
        utf8_bytes = sample_text.encode("utf-8")
        result = decode(utf8_bytes)
        assert result == sample_text

    @pytest.mark.it("when raw_btyes are utf-16 encoded, returns decoded output")
    def test_decoding_utf_16(self, sample_text):
        utf16_bytes = sample_text.encode("utf-16")
        result = decode(utf16_bytes)
        assert result == sample_text

    @pytest.mark.it("when raw_btyes are utf-8-sig encoded, returns decoded output")
    def test_decoding_utf_8_sig(self, sample_text):
        utf8sig_bytes = sample_text.encode("utf-8-sig")
        result = decode(utf8sig_bytes)
        assert result == sample_text

    @pytest.mark.it("when raw_btyes are ISO-8859-1 encoded, returns decoded output")
    def test_decoding_iso_8859_1(self, sample_text):
        utfiso88591_bytes = sample_text.encode("ISO-8859-1")
        result = decode(utfiso88591_bytes)
        assert result == sample_text

    @pytest.mark.it("when raw_btyes are ascii encoded, returns decoded output")
    def test_decoding_ascii(self, sample_text):
        ascii_bytes = sample_text.encode("ascii")
        result = decode(ascii_bytes)
        assert result == sample_text

    @pytest.mark.it("when raw_btyes are cp1252 encoded, returns decoded output")
    def test_decoding_cp1252(self, sample_text):
        cp1252_bytes = sample_text.encode("cp1252")
        result = decode(cp1252_bytes)
        assert result == sample_text

    @pytest.mark.it("when raw_btyes are utf-32 encoded, returns decoded output")
    def test_decoding_utf_32(self, sample_text):
        utf_32_bytes = sample_text.encode("utf-32")
        result = decode(utf_32_bytes)
        assert result == sample_text

    @pytest.mark.it(
        "when raw_btyes have an encoding not supported by csv, json or parquet, raises UnicodeDecodeError"
    )
    def test_decoding_unsupported(self, sample_text):
        unsupported_encoding_bytes = sample_text.encode("shift_jis")
        result = decode(unsupported_encoding_bytes)
        assert result == sample_text
