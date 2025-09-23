import re


def get_bucket_name(path: str):
    if not isinstance(path, str):
        raise TypeError("Path to file must be a string")

    try:
        if isinstance(path, str):
            if path.startswith("s3://"):
                bucket_name = path.split("s3://", 1)[1].split("/", 1)[0]

            elif path.startswith("https://"):
                if path.startswith("https://s3.amazonaws.com"):
                    bucket_name = path.split("https://s3.amazonaws.com/")[1].split(
                        "/", 1
                    )[0]
                else:
                    bucket_name = path.split("https://")[1].split(".", 1)[0]

            elif path.startswith("arn"):
                bucket_name = path.split("arn:aws:s3:::")[1].split("/")[0]

            # checking that bucket_name fulfills aws naming rules (https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucketnamingrules.html):
            if (
                len(bucket_name) > 2
                and len(bucket_name) < 64
                and re.fullmatch(r"[a-z0-9.-]+", bucket_name) is not None
            ):
                return bucket_name

    except Exception:
        raise ValueError("Invalid path provided")
