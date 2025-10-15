import boto3
from src.obfuscator import Obfuscator


def lambda_handler(event, context):
    try:
        obfuscator = Obfuscator(event["file_to_obfuscate"], event["pii_fields"])
        obfuscated_df = obfuscator.get_obfuscated_df()
        obfuscated_bytestream = obfuscator.get_obfuscated_bytestream(obfuscated_df)
        s3_client = boto3.client("s3")
        s3_client.put_object(
            Body=obfuscated_bytestream,
            Bucket=obfuscator.bucket_name,
            Key=f"obfuscated_data/{obfuscator.file_name}",
        )
        return {
            "statusCode": 200,
            "body": f"Obfuscated file successfully uploaded to s3://{obfuscator.bucket_name}/obfuscated_data/{obfuscator.file_name}",
        }
    except Exception as err:
        if hasattr(err, "response") and "Error" in err.response:
            error_message = err.response["Error"].get("Message", str(err))
        else:
            error_message = str(err)
        return {"statusCode": 400, "body": f"Failed to obfuscate file: {error_message}"}
