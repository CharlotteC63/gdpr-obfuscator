import re

def get_bucket_name(path: str):
    if not isinstance(path, str):
        raise TypeError("Path to file must be a string")
    
    bucket_name = None

    try:
        if path.startswith("s3://"):
            bucket_name = path.split("s3://", 1)[1].split("/", 1)[0]

        elif path.startswith("https://"):
            if path.startswith("https://s3.amazonaws.com"):
                bucket_name = path.split("https://s3.amazonaws.com/")[1].split(
                    "/", 1
                )[0]
            else:
                bucket_name = path.split("https://")[1].split(".", 1)[0]

        elif path.startswith("arn:aws:s3:::"):
            bucket_name = path.split("arn:aws:s3:::")[1].split("/")[0]

        else:
            raise ValueError("Unsupported path format")
        
    except (IndexError, ValueError):
        raise ValueError("Invalid path format, could not extract bucket name")

    if not check_validity_of_s3_bucket_name(bucket_name):
        raise ValueError("Invalid bucket name according to AWS rules, see https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucketnamingrules.html")
    
    return bucket_name

def check_validity_of_s3_bucket_name(name: str):
    if not (3 <= len(name) <= 63):
        return False
    if not re.fullmatch(r'[a-z0-9][a-z0-9.-]*[a-z0-9]', name):
        return False
    if '..' in name or '.-' in name or '-.' in name:
        return False
    return True