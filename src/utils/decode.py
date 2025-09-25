def decode(raw_bytes):
    """
    Decodes the binary encoded data (raw bytes) read from an s3 object, by detecting the encoding type.

    Parameters
    ----------
    raw_bytes : str
        Binary encoded data read from the s3 object, yet to be decoded.

    Returns
    ----------
    str
        A bytestring of the decoded file contents.

    Raises
    ----------
    UnicodeDecodeError
        When passed with raw bytes of an encoding type not supported (supported encoding types include:
        utf-8, utf-16, utf-8-sig, ISO-8859-1, ascii, cp1252 and utf-3).

    """
    possible_encoding = [
        "utf-32",
        "utf-8-sig",
        "utf-8",
        "utf-16",
        "ISO-8859-1",
        "ascii",
        "cp1252",
    ]
    for encoding in possible_encoding:
        try:
            return raw_bytes.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError(
        """File encoding type not supported (must be utf-8, utf-16, utf-8-sig,
                             ISO-8859-1, ascii, cp1252 or utf-32 encoded)"""
    )
