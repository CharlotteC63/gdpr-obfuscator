import re


def get_bucket_name(path: str):
    """
    Gets the s3 bucket name from a path, if the path format is valid and supported,
    and the bucket name adheres to the main s3 bucket naming rules published by AWS
    here: https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucketnamingrules.html

    Parameters
    ----------
    path : str
        The path to the location of the file to be obfuscated. 
        Must be in s3://..., arn:..., or https://... format.

    Returns
    ---------- 
    str
        A string of the s3 bucket name.

    Raises
    ----------
    ValueError
        When passed with an unsupported path format.
        When passed with an invalid path format.
        When passed with an invalid bucket name according to AWS rules.
    """
    if not isinstance(path, str):
        raise TypeError("Path to file must be a string")

    bucket_name = None

    try:
        if path.startswith("s3://"):
            bucket_name = path.split("s3://", 1)[1].split("/", 1)[0]

        elif path.startswith("https://"):
            if path.startswith("https://s3.amazonaws.com"):
                bucket_name = path.split("https://s3.amazonaws.com/")[1].split("/", 1)[
                    0
                ]
            else:
                bucket_name = path.split("https://")[1].split(".", 1)[0]

        elif path.startswith("arn:aws:s3:::"):
            bucket_name = path.split("arn:aws:s3:::")[1].split("/")[0]

        else:
            raise ValueError("Unsupported path format")

    except (IndexError, ValueError):
        raise ValueError("Invalid path format, could not extract bucket name")

    if not check_validity_of_s3_bucket_name(bucket_name):
        raise ValueError(
            "Invalid bucket name according to AWS rules, see https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucketnamingrules.html"
        )

    return bucket_name


def check_validity_of_s3_bucket_name(bucket_name: str):
    """
    Checks whether an s3 bucket name is valid, according to AWS rules.

    Parameters
    ----------
    bucket_name : str
        A bucket name to be checked according to the main AWS s3 bucket naming rules.

    Returns
    ---------- 
    bool
        True: if the name passed adheres to s3 bucket naming rules.
        False: if the name passed violates one of the s3 bucket naming rules:
        - contains fewer than 3, or more than 63 characters.
        - contains special characters (<!?/\@#$%&*&+=`~>)
        - contains uppercase characters.
        - contains an underscore.
        - contains two adjacent periods.
    """
    if not (3 <= len(bucket_name) <= 63):
        return False
    if not re.fullmatch(r"[a-z0-9][a-z0-9.-]*[a-z0-9]", bucket_name):
        return False
    if ".." in bucket_name or ".-" in bucket_name or "-." in bucket_name:
        return False
    return True
