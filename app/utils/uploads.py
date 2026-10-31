import secrets
from pathlib import Path

from flask import current_app
from PIL import Image, UnidentifiedImageError
from werkzeug.datastructures import FileStorage


def save_image_upload(upload: FileStorage | None, target_folder: str | None = None) -> str | None:
    if not upload or not upload.filename:
        return None

    extension = Path(upload.filename).suffix.lower().lstrip(".")
    if extension not in current_app.config["ALLOWED_IMAGE_EXTENSIONS"]:
        raise ValueError("Unsupported image type.")

    expected_format = {"jpg": "JPEG", "jpeg": "JPEG", "png": "PNG", "gif": "GIF", "webp": "WEBP"}[extension]
    try:
        image = Image.open(upload.stream)
        if image.format != expected_format:
            raise ValueError("The image contents do not match the file extension.")
        max_pixels = current_app.config["MAX_IMAGE_PIXELS"]
        if image.width * image.height > max_pixels:
            raise ValueError("Image dimensions exceed the allowed limit.")
        image.verify()
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as error:
        raise ValueError("The uploaded file is not a valid supported image.") from error
    finally:
        upload.stream.seek(0)

    folder = Path(target_folder or current_app.config["UPLOAD_FOLDER"])
    folder.mkdir(parents=True, exist_ok=True)
    filename = upload.filename.rsplit("/", 1)[-1]
    safe_name = filename.replace(" ", "_")
    stem = Path(safe_name).stem[:80] or "upload"
    storage_name = f"{stem}-{secrets.token_hex(8)}.{extension}"
    destination = folder / storage_name
    upload.save(destination)
    return storage_name
