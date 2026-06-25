"""Tests for the pure image-validation logic."""

from __future__ import annotations

import io

import pytest
from PIL import Image

from debuggenius.config import AppConfig
from debuggenius.exceptions import ValidationError
from debuggenius.validation import validate_image


def _config(**overrides) -> AppConfig:
    base = dict(api_key="test-key")
    base.update(overrides)
    return AppConfig(**base)


def _png_bytes(size=(64, 48), color=(20, 20, 30)) -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", size, color).save(buffer, format="PNG")
    return buffer.getvalue()


def test_valid_png_passes():
    data = _png_bytes()
    result = validate_image(data, "error.png", _config())
    assert result.mime_type == "image/png"
    assert (result.width, result.height) == (64, 48)


def test_jpeg_extension_maps_to_jpeg_mime():
    buffer = io.BytesIO()
    Image.new("RGB", (10, 10)).save(buffer, format="JPEG")
    result = validate_image(buffer.getvalue(), "shot.JPG", _config())
    assert result.mime_type == "image/jpeg"


def test_empty_file_rejected():
    with pytest.raises(ValidationError):
        validate_image(b"", "x.png", _config())


def test_unsupported_extension_rejected():
    with pytest.raises(ValidationError):
        validate_image(_png_bytes(), "notes.gif", _config())


def test_oversized_file_rejected():
    with pytest.raises(ValidationError):
        validate_image(_png_bytes(), "big.png", _config(max_file_bytes=10))


def test_non_image_bytes_rejected():
    with pytest.raises(ValidationError):
        validate_image(b"this is not an image", "fake.png", _config())


def test_oversized_dimensions_rejected():
    data = _png_bytes(size=(2000, 200))
    with pytest.raises(ValidationError):
        validate_image(data, "wide.png", _config(max_image_dimension=512))
