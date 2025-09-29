import pandas as pd


def obfuscate_pii(all_file_data_df: pd.DataFrame, pii_fields: list):
    """
    Takes a pandas dataframe of a file's contents and obfuscates personally identifiable information. The function
    overwrites PII fields in-place (i.e. it mutates the input, all_file_data_df) for security reasons, so that PII
    details are not stored in memory after the function is run.

    Parameters
    ----------
    all_file_data_df : df
        A pandas dataframe of the file's complete contents.
    pii_fields: lst
        A list of strings of the field names to be obfuscated.

    Returns
    ----------
    obfuscated_data_df
        A dataframe of the file's obduscated contents, with all pii columns' rows replaced
        with the string, '***'.

    """
    if all_file_data_df.empty or not pii_fields:
        return all_file_data_df
    contains_pii = False
    for pii_field in pii_fields:
        if pii_field in all_file_data_df.columns:
            contains_pii = True
            all_file_data_df[pii_field] = "***"
    if contains_pii is False:
        return all_file_data_df
    return all_file_data_df
