import os
import uuid
from dataclasses import dataclass

MIME_TO_EXTENSION = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


@dataclass
class S3File:
    content: bytes
    media_type: str


def generate_uuid_filename(media_type: str) -> str:
    file_id = uuid.uuid4()
    extension = MIME_TO_EXTENSION.get(media_type, ".jpg")

    filename = str(file_id) + extension
    return filename
