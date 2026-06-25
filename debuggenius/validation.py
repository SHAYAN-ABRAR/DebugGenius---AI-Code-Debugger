"""Pure, testable validation for uploaded images.

The function deliberately takes raw ``bytes`` + a filename rather than a
Streamlit ``UploadedFile`` so it can be unit-tested without the framework.
"""

from __future__ import annotations

import io
from dataclasses import dataclass

from PIL import Image, UnidentifiedImageError

from .config import AppConfig
from .exceptions import ValidationError


@dataclass(frozen=True, slots=True)
class ValidatedImage:
    """The result of a successful validation pass."""

    image_bytes: bytes
    mime_type: str
    width: int
    height: int


def _extension(filename: str) -> str:
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""


def validate_image(data: bytes, filename: str, config: AppConfig) -> ValidatedImage:
    """Validate an uploaded image against size, type and decodability rules.

    Parameters
    ----------
    data:
        Raw bytes of the uploaded file.
    filename:
        Original filename (used for the extension / MIME lookup).
    config:
        Active application configuration (limits + allowed types).

    Returns
    -------
    ValidatedImage
        Normalised metadata for a file that is safe to send to the model.

    Raises
    ------
    ValidationError
        If the file is empty, too large, an unsupported type, or not a
        decodable image.
    """

    if not data:
        raise ValidationError(
            "The uploaded file is empty.",
            hint="Re-export your screenshot and try again.",
        )

    if len(data) > config.max_file_bytes:
        limit_mb = config.max_file_bytes / (1024 * 1024)
        raise ValidationError(
            f"That image is {len(data) / (1024 * 1024):.1f} MB — the limit is "
            f"{limit_mb:.0f} MB.",
            hint="Crop the screenshot to just the error, or compress it.",
        )

    ext = _extension(filename)
    mime_type = config.allowed_mime_types.get(ext)
    if mime_type is None:
        allowed = ", ".join(sorted(config.allowed_mime_types)).upper()
        raise ValidationError(
            f"'{ext or 'unknown'}' files aren't supported.",
            hint=f"Use one of: {allowed}.",
        )

    # Confirm the bytes actually decode as the claimed image type.
    try:
        with Image.open(io.BytesIO(data)) as img:
            img.verify()  # cheap integrity check
        with Image.open(io.BytesIO(data)) as img:
            width, height = img.size
    except (UnidentifiedImageError, OSError) as exc:
        raise ValidationError(
            "That file couldn't be read as an image.",
            hint="Make sure it's a real PNG/JPG screenshot, not a renamed file.",
        ) from exc

    longest = max(width, height)
    if longest > config.max_image_dimension:
        raise ValidationError(
            f"The image is {width}×{height}px — that's larger than the "
            f"{config.max_image_dimension}px limit.",
            hint="Downscale the screenshot before uploading.",
        )

    return ValidatedImage(
        image_bytes=data, mime_type=mime_type, width=width, height=height
    )
