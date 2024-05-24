'''\
Lambda function for handling the file download from S3.
'''


import boto3
from botocore.exceptions import ClientError
from http import HTTPStatus
import json
import os

IMAGE_UPLOAD_BUCKET_S3 = os.environ['IMAGE_UPLOAD_BUCKET_S3']

s3 = boto3.client('s3')


def lambda_handler(event, context):
    '''\
    This function takes This function takes filename key from the 
    request inside the event object and uses it get the image from the 
    s3 bucket and return as part of the response.
    
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
    # Get the filename from the event object
    filename = event['filename']
    
    # Download the image from S3
    try:
        response = s3.get_object(Bucket=IMAGE_UPLOAD_BUCKET_S3, 
                                 Key=filename)
    except ClientError as e:
        # Handle the case where the object does not exist
        if e.response['Error']['Code'] == 'NoSuchKey':
            print(f"The object with key '{filename}' does not exist.")
            return {
                'statusCode': HTTPStatus.BAD_REQUEST.value,
                'body': json.dumps({
                    "error_description": "Invalid key provided, key doesn't exist."
                })
            }
        else:
            print(f"Unexpected error: {e}")
    except Exception as e:
        print(e)
        return {
                'statusCode': HTTPStatus.BAD_REQUEST.value,
                'body': json.dumps({
                    "error_description": "Invalid key provided, key doesn't exist."
                })
        }

    # Image found and read successfully from the bucket.
    image_data = response['Body'].read()
    
    return {
        'statusCode': HTTPStatus.OK.value,
        'body': image_data,
        'isBase64Encoded': True,
        'headers': {
            'Content-Type': f'image/{filename.split(".")[-1]}'
        }
    }

