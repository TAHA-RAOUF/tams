import boto3
import os
from botocore.exceptions import NoCredentialsError, ClientError

def get_s3_client():
    return boto3.client(
        's3',
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
        region_name=os.environ.get('AWS_REGION')
    )

def upload_file_to_s3(file_obj, bucket, key, content_type=None):
    s3 = get_s3_client()
    try:
        extra_args = {'ContentType': content_type} if content_type else {}
        s3.upload_fileobj(file_obj, bucket, key, ExtraArgs=extra_args)
        return True, f'https://{bucket}.s3.amazonaws.com/{key}'
    except (NoCredentialsError, ClientError) as e:
        return False, str(e)
