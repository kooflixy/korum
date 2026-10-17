import os
import uuid
from dataclasses import dataclass


@dataclass
class S3File:
    content: bytes
    media_type: str


def generate_uuid_filename(name: str) -> str:
    file_id = uuid.uuid4()

    _, extension = os.path.splitext(name)

    filename = str(file_id) + extension
    return filename
