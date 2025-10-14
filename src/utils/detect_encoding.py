def detect_encoding(raw_bytes: bytes):
    """
    Detects the encoding type of bytes from a file.

    Parameters
    ----------
    raw_bytes : bytes
        Binary encoded data read from the s3 object, yet to be decoded.

    Returns
    ----------
    str
        The name of the encoding that successfully decodes the bytes.

    Raises
    ----------
    UnicodeDecodeError
        When passed with raw bytes of an encoding type not supported (supported encoding types include:
        utf-8, utf-16, utf-8-sig, ISO-8859-1, cp1252 and utf-3).

    """
    try:
        possible_encodings = ["utf-8", "utf-8-sig", "utf-16"]
        for encoding in possible_encodings:
            try:
                decoded = raw_bytes.decode(encoding)
                if "\ufeff" in decoded and encoding != "utf-8-sig":
                    continue
                else:
                    return encoding
            except UnicodeDecodeError:
                continue
    except Exception:
        raise ValueError(
            "Could not decode using utf-8, utf-8-sig or utf-16, check file encoding"
        )
