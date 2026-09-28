from functools import lru_cache
from io import BytesIO

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

from app.core.config import settings


@lru_cache
def client():
    return boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint_url,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
        region_name=settings.s3_region,
        config=Config(signature_version="s3v4"),
    )


def ensure_bucket() -> None:
    try:
        client().head_bucket(Bucket=settings.s3_bucket)
    except ClientError:
        client().create_bucket(Bucket=settings.s3_bucket)


def put(key: str, data: bytes, mime_type: str) -> None:
    ensure_bucket()
    client().upload_fileobj(BytesIO(data), settings.s3_bucket, key, ExtraArgs={"ContentType": mime_type})


def get(key: str) -> bytes:
    return client().get_object(Bucket=settings.s3_bucket, Key=key)["Body"].read()


def delete(key: str) -> None:
    client().delete_object(Bucket=settings.s3_bucket, Key=key)
