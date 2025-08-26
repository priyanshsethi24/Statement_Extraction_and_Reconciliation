import os
import boto3
from common.logs import logger
from dotenv import load_dotenv

load_dotenv()

aws_access_key_id = os.getenv('aws_access_key_id')
aws_secret_access_key = os.getenv('aws_secret_access_key')
aws_region_name = os.getenv('aws_region')

class S3HelperNew:
    def __init__(self) -> None:
        '''
        Initializes the S3Helper object.
        '''

        self.s3_client = boto3.client(
            's3',
            region_name=aws_region_name,  # Specified the region for the S3 client
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )

    def download_file_from_s3(self, bucket_name, key: str, version_id: str, file_name: str) -> None:
        '''
        Downloads a file from S3 bucket.
        '''
        try:
            logger.debug(
                f"Downloading file from S3: Bucket - '{bucket_name}', Object - '{key}', Local - '{file_name}'")
            response = self.s3_client.get_object(
                Bucket=bucket_name,
                Key=key,
                VersionId=version_id
            )

            with open(file_name, 'wb') as f:
                f.write(response['Body'].read())

        except Exception as e:
            logger.exception(
                f"Exception in download_file_from_s3(): File - '{key}', S3 bucket - '{bucket_name}', to - '{file_name}'")
            raise e

    def upload_file_to_s3(self, bucket_name, file_name: str, output_file_path: str) -> None:
        '''
        Uploads a file to S3 bucket.
        '''
        try:
            # s3_client.upload_file(file_name, bucket_name, object_name)
            with open(file_name, "rb") as f:
                response = self.s3_client.put_object(
                    Bucket=bucket_name,
                    Key=output_file_path,
                    Body=f
                )

            version_id = response.get("VersionId")
            logger.debug(
                f"File '{file_name}' uploaded to S3 bucket '{bucket_name}' as '{output_file_path}'.")
            return version_id
        except Exception as e:
            logger.exception(
                f"Exception in upload_file_to_s3(): File - '{file_name}', S3 bucket - '{bucket_name}'.")
            raise e
