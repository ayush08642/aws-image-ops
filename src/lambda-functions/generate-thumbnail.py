"""\
Lambda function for handling thumbnail generation out of the uploaded files.
"""

import boto3
from http import HTTPStatus
from io import BytesIO
import json
import os
from PIL import Image


IMAGE_UPLOAD_BUCKET_S3 = os.environ["IMAGE_UPLOAD_BUCKET_S3"]
THUMBNAIL_BUCKET_S3 = f"{IMAGE_UPLOAD_BUCKET_S3}/thumbnail/"
THUMBNAIL_SIZE = (100, 100)

s3 = boto3.client("s3")


def thumbnail_generator_handler(event, context):
    """\
    This function takes the message and filename from the SQS using 
    event object and generates a thumbnail for the given image using 
    PIL module.
    
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
    # Get the message from the SQS queue
    message = event["Records"][0]
    filename = message["body"]

    # Download the image from S3
    response = s3.get_object(Bucket=IMAGE_UPLOAD_BUCKET_S3, 
                             Key=filename)
    image_data = response["Body"].read()

    # Generate the thumbnail
    image = Image.open(BytesIO(image_data))
    image.thumbnail(THUMBNAIL_SIZE)

    # Generate the thumbnail filename
    thumbnail_filename = f"thumbnail_{filename}"

    # Saving the image in memory.
    thumbnail_data = BytesIO()
    image.save(thumbnail_data, 
               format="JPEG")

    # Upload the thumbnail to S3
    s3.put_object(
        Bucket=THUMBNAIL_BUCKET_S3,
        Key=thumbnail_filename,
        Body=thumbnail_data.getvalue(),
    )

    return {
        "statusCode": HTTPStatus.OK.value,
        "body": json.dumps({
            "message": "Thumbnail generated successfully"
            }),
    }

