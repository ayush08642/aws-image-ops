"""\
Lambda function for downloading the thumbnail from s3 bucket.
"""

import json
import boto3
from botocore.exceptions import ClientError
from http import HTTPStatus
import os

IMAGE_UPLOAD_BUCKET_S3 = os.environ["IMAGE_UPLOAD_BUCKET_S3"]
THUMBNAIL_BUCKET_S3 = f"{IMAGE_UPLOAD_BUCKET_S3}/thumbnail/"

s3 = boto3.client("s3")


def download_thumbnail_handler(event, context):
    """\
    This lambda function downloads the thumbnail for the relevant image
    from the s3 bucket.
    
    Args:
        event: An event is a JSON-formatted document that contains 
                data for a Lambda function to process. Usually of 
                type dict.
        context: This object provides methods and properties that 
                provide information about the invocation, function, and 
                runtime environment.
    
    Returns:
        dict: This dictionary will be turned into a JSON response later.
    
    Raises:
        None
    """
    # Get the filename from the request
    filename = event["filename"]

    # Generate the thumbnail filename
    thumbnail_filename = f"thumbnail_{filename}"

    # Download the thumbnail from S3
    try:
        response = s3.get_object(Bucket=THUMBNAIL_BUCKET_S3, 
                                 Key=thumbnail_filename)
    except ClientError as e:
        # Handle the case where the object does not exist
        if e.response["Error"]["Code"] == "NoSuchKey":
            print(f"The object with key '{filename}' does not exist.")
            return {
                "statusCode": HTTPStatus.BAD_REQUEST.value,
                "body": json.dumps(
                    {"error_description": "Invalid key provided, key doesn't exist."}
                ),
            }
        else:
            print(f"Unexpected error: {e}")
    except Exception as e:
        print(e)
        return {
            "statusCode": HTTPStatus.BAD_REQUEST.value,
            "body": json.dumps(
                {"error_description": "Invalid key provided, key doesn't exist."}
            ),
        }

    # If thumbnail is found in bucket, read and return the thumbnail.
    thumbnail_data = response["Body"].read()

    return {
        "statusCode": HTTPStatus.OK.value,
        "body": thumbnail_data,
        "isBase64Encoded": True,
        "headers": {"Content-Type": "image/jpeg"},
    }
