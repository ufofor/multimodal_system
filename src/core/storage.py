"""S3 storage — upload, list, download, delete for DocIntel files."""
import os
import boto3


def _client():
    return boto3.client(
        "s3",
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
        region_name=os.environ.get("AWS_REGION", "us-east-1"),
    )


def _bucket() -> str:
    return os.environ["S3_BUCKET_NAME"]


def upload_bytes(data: bytes, s3_key: str) -> None:
    _client().put_object(Bucket=_bucket(), Key=s3_key, Body=data)


def list_files() -> list[str]:
    resp = _client().list_objects_v2(Bucket=_bucket())
    return [obj["Key"] for obj in resp.get("Contents", [])]


def download_bytes(s3_key: str) -> bytes:
    obj = _client().get_object(Bucket=_bucket(), Key=s3_key)
    return obj["Body"].read()


def delete_all_files() -> None:
    client = _client()
    bucket = _bucket()
    resp = client.list_objects_v2(Bucket=bucket)
    objects = resp.get("Contents", [])
    if objects:
        client.delete_objects(
            Bucket=bucket,
            Delete={"Objects": [{"Key": obj["Key"]} for obj in objects]},
        )
