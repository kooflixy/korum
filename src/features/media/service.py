from dataclasses import dataclass

import magic
from fastapi import File, HTTPException, UploadFile, status


@dataclass
class ValidatedFile:
    file: UploadFile
    mime_type: str


def validate_file(max_size: int, allowed_mime_types: set[str]):
    async def validator(upload_file: UploadFile = File(...)) -> ValidatedFile:
        if upload_file.size and upload_file.size > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                detail="Медиафайл слишком большой",
            )

        mime_type = magic.from_buffer(await upload_file.read(2048), mime=True)

        if mime_type not in allowed_mime_types:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="Неподдерживаемый формат медиафайла",
            )

        await upload_file.seek(0)

        return ValidatedFile(upload_file, mime_type)

    return validator
