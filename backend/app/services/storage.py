import boto3
from botocore.client import Config

from app.core.config import settings


def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=f"http://{settings.minio_endpoint}",
        aws_access_key_id=settings.minio_access_key,
        aws_secret_access_key=settings.minio_secret_key,
        config=Config(signature_version="s3v4"),
        region_name="us-east-1",
    )


def ensure_bucket_exists():
    client = get_s3_client()
    buckets = client.list_buckets().get("Buckets", [])
    bucket_names = [b["Name"] for b in buckets]
    if settings.minio_bucket not in bucket_names:
        client.create_bucket(Bucket=settings.minio_bucket)


def upload_fileobj(file_obj, object_name: str, content_type: str | None = None):
    client = get_s3_client()
    extra_args = {}
    if content_type:
        extra_args["ContentType"] = content_type

    client.upload_fileobj(
        Fileobj=file_obj,
        Bucket=settings.minio_bucket,
        Key=object_name,
        ExtraArgs=extra_args,
    )

    return object_name