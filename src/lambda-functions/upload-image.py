'''\
Lambda function for handling the file upload to S3 and adding a message to 
SQS for thumbnail generation, use-case.
'''


import boto3
from http import HTTPStatus
from io import BytesIO
import json
import os
from PIL import Image

IMAGE_UPLOAD_BUCKET_S3 = os.environ['IMAGE_UPLOAD_BUCKET_S3']
SQS_QUEUE_URL = os.getenv['SQS_QUEUE_URL']

s3 = boto3.client('s3')
sqs = boto3.client('sqs')


def file_upload_handler(event, context):
    '''\
    This function takes the uploaded image from the event object and 
    validates the image format and when found valid, it uploads the 
    image to S3 bucket as well as sends a message SQS to generate a 
    thumnail out of the uploaded image.
    
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
    '''
    # Getting the image data from the event object.
    image_data = event['image_data']

    # Decode the image data.
    image_bytes = BytesIO(image_data)

    # Validate image format for PNG and JPEG type.
    try:
        img = Image.open(image_bytes)
        if img.format not in ['PNG', 'JPEG']:
            return {
                "statusCode": HTTPStatus.BAD_REQUEST.value,
                "body": json.dumps({
                    "error_description": "Invalid image format. Only PNG and JPEG formats are allowed"
                })
            }
    except Exception as e:
        return {
            "statusCode": HTTPStatus.BAD_REQUEST.value,
            "body": json.dumps({
                                "error_description": "Error processing the image",
                                "traceback": e
            })
        }

    # Generate a unique filename for the uploaded image.
    filename = f"{event['user_id']}/{event['image_id']}.{img.format.lower()}"
    
    # Upload the image to s3 bucket
    s3.put_object(Bucket=IMAGE_UPLOAD_BUCKET_S3, 
                  Key=filename, 
                  Body=image_data)
    
    # Add a message to the SQS queue for thumbnail generation
    sqs.send_message(QueueUrl=SQS_QUEUE_URL,
                     MessageBody=filename)
    return {
        'statusCode': HTTPStatus.OK.value,
        'body': json.dumps({'message': 'Image uploaded successfully'})
    }

