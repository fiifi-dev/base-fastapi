import json
import io
import pathlib
import random
from PIL import Image
import urllib3
from urllib3 import exceptions
import mimetypes
import minio
from datetime import timedelta
from minio import Minio
from app.core.config import settings
from fastapi import UploadFile


class MinioStorage:
    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
        )

        self.secret_key = settings.MINIO_SECRET_KEY
        self.endpoint = settings.MINIO_ENDPOINT
        self.access_key = settings.MINIO_ACCESS_KEY
        self.bucket = settings.MINIO_BUCKET
        self.locations = settings.MINIO_PUBLIC_LOCATIONS

    def _guess_content_type(self, object_path: str, content: UploadFile):
        if hasattr(content, "content_type") and content.content_type:
            return content.content_type

        guess = mimetypes.guess_type(object_path)[0]

        if guess is None:
            return "application/octet-stream"  # default

        return guess

    def _exists(self, object_path: str) -> bool:
        """Check if an object with name already exists"""

        try:
            if self.client.stat_object(self.bucket, object_path):
                return True
            return False
        except minio.error.S3Error:
            return False
        except (minio.error.ServerError, exceptions.MaxRetryError):
            raise AttributeError(
                f"Could not stat object ({object_path}) in bucket ({self.bucket})"
            )

    def _is_object_public(self, name: str) -> bool:
        """Check if an object is public"""
        folder = pathlib.Path(name).parts[0]

        if folder in self.locations:
            return True

        return False

    def _get_available_name(self, stem: str, ext, dir="") -> str:

        available_name = f"{dir}{'/' if dir else '' }{stem}{ext}"

        while self._exists(available_name):
            nums = "".join(random.choices("0123456789", k=5))
            available_name = f"{dir}{'/' if dir else '' }{stem}{nums}{ext}"

        return available_name

    def url(self, object_path: str):
        """
        Returns url to object.
        If bucket is public, direct link is provided.
        if bucket is private, a pre-signed link is provided.
        :param name: (str) file path + file name + suffix
        :return: (str) URL to object
        """
        is_object_public = self._is_object_public(object_path)

        if is_object_public:
            return f"{self.endpoint}/{self.bucket}/{object_path}"

        try:
            u = self.client.presigned_get_object(
                bucket_name=self.bucket,
                object_name=object_path.encode("utf-8"),
                expires=timedelta(
                    days=settings.MINIO_URL_EXPIRY_DAYS
                ),  # Default is 7 days
            )
            return u
        except exceptions.MaxRetryError:
            raise ConnectionError(
                "Couldn't connect to Minio. Check django_minio_backend parameters in Django-Settings"
            )

    def open(self, object_path, mode="rb", **kwargs) -> UploadFile:
        res: urllib3.response.HTTPResponse = urllib3.response.HTTPResponse()
        if mode != "rb":
            raise ValueError(
                "Files retrieved from MinIO are read-only. Use save() method to override contents"
            )
        try:

            res = self.client.get_object(self.bucket, object_path, **kwargs)
            content_bytes: io.BytesIO = io.BytesIO(res.read())
            content_length: int = len(content_bytes.getvalue())

            file = UploadFile(
                io.BytesIO(res.read()),
                filename=object_path,
                size=content_length,
            )
        finally:
            res.close()
            res.release_conn()
        return file

    def save(self, object_path: str, content: UploadFile, is_thumb=False) -> str:
        # Upload object
        file_path: pathlib.Path = pathlib.Path(object_path)
        content_bytes: io.BytesIO = io.BytesIO(content.file.read())
        content_length: int = len(content_bytes.getvalue())

        stem = file_path.stem if not is_thumb else f"thumb_{file_path.stem}"
        ext = file_path.suffix
        dir = file_path.parent

        file_name = self._get_available_name(stem, ext, dir.as_posix())

        self.client.put_object(
            bucket_name=self.bucket,
            object_name=file_name,
            data=content_bytes,
            length=content_length,
            content_type=self._guess_content_type(object_path, content),
        )

        return file_name

    def generate_thumbnail(self, object_path: str, content: UploadFile):
        THUMBNAIL_SIZE = (300, 300)
        image = Image.open(content.file)
        image.thumbnail(THUMBNAIL_SIZE, Image.ANTIALIAS)
        temp_handle = io.BytesIO()
        image.save(temp_handle, image.format)
        temp_handle.seek(0)

        size = len(temp_handle.read())

        temp_handle.seek(0)

        new_file = UploadFile(
            temp_handle,
            filename=content.filename,
            size=size,
        )

        saved_path = self.save(object_path, new_file, True)
        temp_handle.close()
        return saved_path

    def delete(self, object_path: str):
        self.client.remove_object(
            bucket_name=self.bucket,
            object_name=object_path,
        )

    def check_bucket_existence(self):
        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(bucket_name=self.bucket)
            self.create_bucket_access_policy()

    def create_bucket(self):
        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)

    def create_bucket_access_policy(self):
        """Set a custom bucket policy for static files"""
        bucket = self.bucket

        access_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "PublicBucket",
                    "Effect": "Allow",
                    "Principal": {"AWS": ["*"]},
                    "Action": ["s3:GetBucketLocation", "s3:ListBucket"],
                    "Resource": [f"arn:aws:s3:::{bucket}"],
                },
                {
                    "Sid": "PublicRead",
                    "Effect": "Allow",
                    "Principal": {"AWS": ["*"]},
                    "Action": ["s3:GetObject", "s3:GetObjectVersion"],
                    "Resource": [
                        f"arn:aws:s3:::{bucket}/{loc}*" for loc in self.locations
                    ],
                },
            ],
        }

        self.client.set_bucket_policy(
            bucket_name=bucket, policy=json.dumps(access_policy)
        )
