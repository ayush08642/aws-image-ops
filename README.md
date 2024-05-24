# aws-image-ops
This repository contains implementation of a module which is responsible for supporting image upload, thumbnail generation, and storage in the Cloud.

For implementing the above module, we'll require the following AWS services:

1. Identity and Accesss Management (IAM)
2. Simple Storage Service (S3)
3. API-Gateway
4. Lambda
5. Simpe Queue Service (SQS)
6. CloudWatch (optional service for checking logs)

## High-Level Architecture

1. **API Gateway**: Handles incoming requests for image upload, download, and thumbnail download.
2. **Lambda Functions**:
> * **Upload Image Function**: Handles image upload to S3 and adds a message to SQS queue for thumbnail generation.
> * **Download Image Function**: Download the image from S3 bucket.
> * **Generate Thumbnail Function**: Generates thumbnails for uploaded images and stores them in S3.
> * **Download Thumbnail Function**: Downloads the thumbnail for the image.

3. **SQS Queue**: Stores messages for thumbnail generation.
4. **S3 Bucket**: Stores uploaded images and generated thumbnails.