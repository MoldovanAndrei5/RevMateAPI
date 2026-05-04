import boto3
import uuid
import os

BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
REGION = os.getenv("S3_REGION")

s3_client = boto3.client("s3", region_name=REGION)

def generate_presigned_upload_url(folder: str, file_name: str, content_type: str, expires_in: int = 900) -> dict:
    file_key = f"{folder}/{uuid.uuid4()}_{file_name}"

    upload_url = s3_client.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": BUCKET_NAME,
            "Key": file_key,
            "ContentType": content_type,
        },
        ExpiresIn=expires_in  # 15 minutes
    )

    return {
        "upload_url": upload_url,
        "file_key": file_key
    }


def generate_presigned_download_url(file_key: str, expires_in: int = 3600) -> str:
    return s3_client.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": BUCKET_NAME,
            "Key": file_key,
        },
        ExpiresIn=expires_in  # 1 hour
    )


def delete_file(file_key: str) -> None:
    s3_client.delete_object(Bucket=BUCKET_NAME, Key=file_key)