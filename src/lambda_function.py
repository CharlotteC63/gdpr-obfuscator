import boto3
import os

if 'LAMBDA_TASK_ROOT' in os.environ:
    # Running in Lambda (deployment)
    from obfuscator import Obfuscator
else:
    # Running locally (dev)
    from src.obfuscator import Obfuscator


def lambda_handler(event, context):
    """Lambda handler that finds a file in an s3 bucket (when supplied with the pathway),detects the file type
    (csv, json or parquet) and encoding type (utf-8, utf-sig-8 or utf-16), and uses this information to turn the
    contents of the file into a pandas dataframe. It then obfuscates the columns of this dataframe that contain
    personally identifiable information, PII (as identified by the list of PII columns supplied by the user),
    then turns this obfuscated dataframe back into bytes, and uses boto3 put_object to upload the obfusated file back
    to the original s3 bucket, inside a key labelled 'obfuscated_data'.

    Args:
        event (dict): a json string containing two keys:
            - `file_to_obfuscate` (required): The s3 location of the required file for obfuscation (as a string)
            - `pii_fields` (optional): A list of the PII fields to obfuscate (as a list of strings)
        context (dict): an AWS Lambda context object (unused but required by AWS)

    Return:
        dict: A dictionary to indicate whether or not the obfuscated file was successfully uploaded to s3,
        with the appropriate status code (200 for success, 400 for failure), and message. If the extraction
        of the file, obfuscation, or upload to s3 fails, the error message in the dict returned will inform
        the user of the reason for the failure.
    """
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
