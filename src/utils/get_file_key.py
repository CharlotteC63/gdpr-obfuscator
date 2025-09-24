from src.utils.get_bucket_name import get_bucket_name


def get_file_key(path):
    """
    Gets the key of an S3 object from its file path.

    Parameters
    ----------
    path : str
        The path to the location of the file to be obfuscated. 
        Must be in s3://..., arn:..., or https://... format.

    Returns
    ---------- 
    str
        A string of the file key.

    Raises
    ----------
    ValueError
        - When the bucket name in the path is invalid.
        - When the path format is not recognised.
        - When the path contains no key after the bucket name.
        - When the key exceeds the maximum length of 1,024 bytes (UTF-8 encoded), 
          according to AWS published rules.
    
    """
    bucket_name = get_bucket_name(path)
    key = None

    if not bucket_name:
        raise ValueError("Could not extract key name as bucket name is invalid")

    if path.startswith(("s3://", "arn")):
        key = path.split(f"{bucket_name}/", 1)[1]

    if path.startswith("https://"):
        if path.startswith("https://s3.amazonaws.com/"):
            key = path.split(f"{bucket_name}/", 1)[1]
        else:
            key = path.split(f"{bucket_name}.s3.amazonaws.com/", 1)[1]

    if key == "":
        raise ValueError(
            "Key not found after bucket name"
        )

    if len(key.encode("utf-8")) > 1024:
        raise ValueError(
            "S3 object key exceeds the maximum length of 1,024 bytes (UTF-8 encoded)"
        )

    return key
        