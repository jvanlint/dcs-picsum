import os
import random
from pathlib import Path
from io import BytesIO
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse
from PIL import Image

app = FastAPI(title="Random Screenshot API", version="1.0.0")

MEDIA_FOLDER = Path("media")
SUPPORTED_FORMATS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}


def get_random_image() -> Path:
    """Get a random image file from the media folder."""
    if not MEDIA_FOLDER.exists():
        raise HTTPException(status_code=500, detail="Media folder not found")

    image_files = [
        f for f in MEDIA_FOLDER.iterdir()
        if f.is_file() and f.suffix.lower() in SUPPORTED_FORMATS
    ]

    if not image_files:
        raise HTTPException(status_code=404, detail="No images found in media folder")

    return random.choice(image_files)


def resize_image(image: Image.Image, width: Optional[int], height: Optional[int]) -> Image.Image:
    """Resize image to specified dimensions while maintaining aspect ratio if only one dimension is provided."""
    if width is None and height is None:
        return image

    original_width, original_height = image.size

    if width and height:
        return image.resize((width, height), Image.Resampling.LANCZOS)
    elif width:
        aspect_ratio = original_height / original_width
        new_height = int(width * aspect_ratio)
        return image.resize((width, new_height), Image.Resampling.LANCZOS)
    else:
        aspect_ratio = original_width / original_height
        new_width = int(height * aspect_ratio)
        return image.resize((new_width, height), Image.Resampling.LANCZOS)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Random Screenshot API",
        "endpoints": {
            "/random": "Get a random screenshot",
            "/random?width=800&height=600": "Get a random screenshot resized to specific dimensions"
        }
    }


@app.get("/random")
async def get_random_screenshot(
    width: Optional[int] = Query(None, gt=0, le=4000, description="Desired width in pixels"),
    height: Optional[int] = Query(None, gt=0, le=4000, description="Desired height in pixels")
):
    """
    Get a random screenshot from the media folder.

    Optionally resize the image by providing width and/or height parameters.
    If only one dimension is provided, aspect ratio is maintained.
    """
    image_path = get_random_image()

    try:
        with Image.open(image_path) as img:
            if img.mode in ("RGBA", "LA", "P"):
                img = img.convert("RGB")

            if width or height:
                img = resize_image(img, width, height)

            img_byte_arr = BytesIO()
            img.save(img_byte_arr, format="JPEG", quality=85)
            img_byte_arr.seek(0)

            return StreamingResponse(
                img_byte_arr,
                media_type="image/jpeg",
                headers={"X-Image-Source": image_path.name}
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    image_count = len([
        f for f in MEDIA_FOLDER.iterdir()
        if f.is_file() and f.suffix.lower() in SUPPORTED_FORMATS
    ]) if MEDIA_FOLDER.exists() else 0

    return {
        "status": "healthy",
        "media_folder_exists": MEDIA_FOLDER.exists(),
        "image_count": image_count
    }
