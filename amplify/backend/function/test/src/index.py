import os
import time

import boto3
import decimal
from botocore.exceptions import ClientError
from chalice import BadRequestError,Chalice
from gql import gql
import datetime
import json
from threading import Thread


# Create instances of the required clients
app = Chalice(app_name="testData")
s3 = boto3.client('s3')
BUCKET_NAME = os.environ.get('S3_BUCKET_NAME', 'dresumetest')

def default_serializer(o):
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.isoformat()
    if isinstance(o, decimal.Decimal):
        return str(o)


@app.middleware('all')
def my_middleware(event, get_response):
    if '{proxy+}' in event.path:
        event.context['resourcePath'] = event.path.replace(
            '{proxy+}', event.uri_params['proxy'])
        event.path = event.path.replace('{proxy+}', event.uri_params['proxy'])
    response = get_response(event)
    response.body = json.loads(json.dumps(response.body, default=default_serializer))
    print(f"Response.body:- {response.body}")
    print("response-------: ", response)
    return response

@app.route('/generatepresignedurl', methods=['POST'], cors=True, content_types=['application/json'])
def generate_presigned_url():
    request = app.current_request
    # Get the filename and filetype from the request body
    data = request.json_body
    file_name = data.get('fileName')
    file_type = data.get('fileType')

    if not file_name or not file_type:
        return {'message': 'File name and file type are required'}, 400

    try:
        # Generate a presigned URL to upload a file to S3
        presigned_url = generate_presigned_url_to_s3(file_name, file_type)
        return {'uploadURL': presigned_url}
    except ClientError as e:
        return {'message': str(e)}, 500


def generate_presigned_url_to_s3(file_name, file_type):
    """Generate a presigned URL to upload a file to S3"""
    try:
        # Generate the presigned URL
        presigned_url = s3.generate_presigned_url('put_object',
                                                          Params={'Bucket': BUCKET_NAME,
                                                                  'Key': file_name,
                                                                  'ContentType': file_type},
                                                          ExpiresIn=3600)  # URL expires in 1 hour
        return presigned_url
    except ClientError as e:
        raise Exception(f"Error generating presigned URL: {e}")
