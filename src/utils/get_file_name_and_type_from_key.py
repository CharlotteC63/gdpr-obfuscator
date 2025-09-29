def get_file_name_and_type_from_key(key: str):
    split_by_slash = key.split("/")
    name = split_by_slash[len(split_by_slash) - 1]
    split_by_period = key.split(".")
    file_type = split_by_period[len(split_by_period) - 1]
    if file_type in ("csv", "json", "parquet"):
        return {"name": name, "file_type": file_type}
    else:
        raise ValueError("file_type not supported (must be csv, json or parquet)")
