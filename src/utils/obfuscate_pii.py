def obfuscate_pii(file_contents: list, pii_fields: list):
    """
    Takes a dict of data and obfuscates personally identifiable information. The function overwrites PII
    fields in-place (i.e. it mutates the input, file_contents) for security reasons, so that PII details
    are not stored in memory.

    Parameters
    ----------
    file_contents : lst
        A list of dictionaries of the file's complete contents.
    pii_fields: lst
        A list of the fields to be obfuscated.

    Returns
    ----------
    dict
        A list of the file's obduscated contents within dictionaries (with all pii keys' values replaced
        with the string, '***').

    """
    if [] in (file_contents, pii_fields):
        return file_contents

    for person in file_contents:
        for field in pii_fields:
            if field in person:
                person[field] = "***"

    return file_contents
