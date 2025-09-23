from src.utils.get_bucket_name import get_bucket_name


def get_file_key(path):
    bucket_name = get_bucket_name(path)
    key = None
    if path.startswith(("s3://", "arn")):
        try:
            key = path.split(f"{bucket_name}/", 1)[1]
        except IndexError:
            raise ValueError(
                "Invalid S3 path format — key not found after bucket name."
            )

    elif path.startswith("https://"):
        if path.startswith("https://s3.amazonaws.com/"):
            try:
                key = path.split(f"{bucket_name}/", 1)[1]
            except IndexError:
                raise ValueError(
                    "Invalid S3 URL format — key not found after bucket name."
                )
        else:
            try:
                key = path.split(f"{bucket_name}.s3.amazonaws.com/", 1)[1]
            except IndexError:
                raise ValueError("Invalid S3 custom domain format — key not found.")

    else:
        raise ValueError(
            "Path format not recognised. Must be s3://..., arn:..., or https://..."
        )

    if len(key.encode("utf-8")) > 1024:
        raise ValueError(
            "S3 object key exceeds the maximum length of 1,024 bytes (UTF-8 encoded)"
        )

    return key
