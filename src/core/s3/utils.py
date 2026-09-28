import uuid
import os

def generate_uuid_filename(name: str) -> str:
    file_id = uuid.uuid4()

    _, extension = os.path.splitext(name)

    filename = file_id + extension
    return filename