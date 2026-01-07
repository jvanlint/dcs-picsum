import os
import random
import json
from pathlib import Path
from io import BytesIO
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse
from PIL import Image

app = FastAPI(title="Random Screenshot API", version="1.0.0")

MEDIA_FOLDER = Path("media")
SUPPORTED_FORMATS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}
METADATA_FILE = MEDIA_FOLDER / "metadata.json"
AVATARS_FOLDER = MEDIA_FOLDER / "avatars"

# Global metadata cache
_metadata_cache: Optional[Dict[str, Any]] = None


def load_metadata() -> Dict[str, Any]:
    """Load metadata from JSON file. Uses cache if available."""
    global _metadata_cache

    if _metadata_cache is not None:
        return _metadata_cache

    if not METADATA_FILE.exists():
        return {"schema": {}, "images": {}}

    try:
        with open(METADATA_FILE, "r") as f:
            _metadata_cache = json.load(f)
            return _metadata_cache
    except Exception as e:
        print(f"Warning: Could not load metadata: {e}")
        return {"schema": {}, "images": {}}


def filter_images_by_metadata(
    aircraft: Optional[str] = None,
    location: Optional[str] = None,
    time_of_day: Optional[str] = None,
    weather: Optional[str] = None,
    tags: Optional[str] = None
) -> List[str]:
    """Filter images based on metadata criteria."""
    metadata = load_metadata()
    images_metadata = metadata.get("images", {})

    # Get all image files
    all_images = [
        f.name for f in MEDIA_FOLDER.iterdir()
        if f.is_file() and f.suffix.lower() in SUPPORTED_FORMATS
    ]

    # If no metadata or no filters, return all images
    if not images_metadata or not any([aircraft, location, time_of_day, weather, tags]):
        return all_images

    # Parse tags parameter (comma-separated)
    tag_list = [t.strip() for t in tags.split(",")] if tags else []

    # Filter images
    filtered = []
    for image_name in all_images:
        image_meta = images_metadata.get(image_name, {})

        # Check each filter criterion
        if aircraft and aircraft not in image_meta.get("aircraft", []):
            continue

        if location and image_meta.get("location") != location:
            continue

        if time_of_day and image_meta.get("time_of_day") != time_of_day:
            continue

        if weather and image_meta.get("weather") != weather:
            continue

        if tag_list:
            image_tags = image_meta.get("tags", [])
            if not all(tag in image_tags for tag in tag_list):
                continue

        filtered.append(image_name)

    return filtered


def get_random_image(
    aircraft: Optional[str] = None,
    location: Optional[str] = None,
    time_of_day: Optional[str] = None,
    weather: Optional[str] = None,
    tags: Optional[str] = None
) -> tuple[Path, Dict[str, Any]]:
    """Get a random image file from the media folder, optionally filtered by metadata."""
    if not MEDIA_FOLDER.exists():
        raise HTTPException(status_code=500, detail="Media folder not found")

    # Get filtered image list
    filtered_images = filter_images_by_metadata(aircraft, location, time_of_day, weather, tags)

    if not filtered_images:
        raise HTTPException(
            status_code=404,
            detail="No images found matching the specified criteria"
        )

    # Select random image
    selected_image = random.choice(filtered_images)
    image_path = MEDIA_FOLDER / selected_image

    # Get metadata for this image
    metadata = load_metadata()
    image_metadata = metadata.get("images", {}).get(selected_image, {})

    return image_path, image_metadata


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


def get_random_avatar() -> Path:
    """Get a random avatar from the avatars folder."""
    if not AVATARS_FOLDER.exists():
        raise HTTPException(status_code=500, detail="Avatars folder not found")

    avatar_files = [
        f for f in AVATARS_FOLDER.iterdir()
        if f.is_file() and f.suffix.lower() in SUPPORTED_FORMATS
    ]

    if not avatar_files:
        raise HTTPException(status_code=404, detail="No avatars found in avatars folder")

    return random.choice(avatar_files)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Random Screenshot API",
        "endpoints": {
            "/random": "Get a random screenshot",
            "/random?width=800&height=600": "Get a random screenshot resized to specific dimensions",
            "/random?aircraft=F-18C": "Get a random screenshot filtered by aircraft",
            "/random?aircraft=F-18C&location=carrier&width=800": "Combine filters with resizing",
            "/avatar": "Get a random avatar",
            "/avatar?width=200&height=200": "Get a random avatar resized to specific dimensions",
            "/tags": "List available metadata schema and tag counts",
            "/health": "Health check endpoint"
        }
    }


@app.get("/random")
async def get_random_screenshot(
    width: Optional[int] = Query(None, gt=0, le=4000, description="Desired width in pixels"),
    height: Optional[int] = Query(None, gt=0, le=4000, description="Desired height in pixels"),
    aircraft: Optional[str] = Query(None, description="Filter by aircraft type (e.g., F-18C)"),
    location: Optional[str] = Query(None, description="Filter by location (e.g., carrier, desert)"),
    time_of_day: Optional[str] = Query(None, description="Filter by time of day (e.g., day, night)"),
    weather: Optional[str] = Query(None, description="Filter by weather (e.g., clear, cloudy)"),
    tags: Optional[str] = Query(None, description="Filter by tags, comma-separated (e.g., combat,landing)")
):
    """
    Get a random screenshot from the media folder.

    Optionally filter by metadata (aircraft, location, time_of_day, weather, tags).
    Optionally resize the image by providing width and/or height parameters.
    If only one dimension is provided, aspect ratio is maintained.
    """
    image_path, image_metadata = get_random_image(
        aircraft=aircraft,
        location=location,
        time_of_day=time_of_day,
        weather=weather,
        tags=tags
    )

    try:
        with Image.open(image_path) as img:
            if img.mode in ("RGBA", "LA", "P"):
                img = img.convert("RGB")

            if width or height:
                img = resize_image(img, width, height)

            img_byte_arr = BytesIO()
            img.save(img_byte_arr, format="JPEG", quality=85)
            img_byte_arr.seek(0)

            # Build response headers with metadata
            headers = {"X-Image-Source": image_path.name}
            if image_metadata:
                if image_metadata.get("aircraft"):
                    headers["X-Image-Aircraft"] = ",".join(image_metadata["aircraft"])
                if image_metadata.get("location"):
                    headers["X-Image-Location"] = image_metadata["location"]
                if image_metadata.get("time_of_day"):
                    headers["X-Image-TimeOfDay"] = image_metadata["time_of_day"]
                if image_metadata.get("weather"):
                    headers["X-Image-Weather"] = image_metadata["weather"]
                if image_metadata.get("tags"):
                    headers["X-Image-Tags"] = ",".join(image_metadata["tags"])

            return StreamingResponse(
                img_byte_arr,
                media_type="image/jpeg",
                headers=headers
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")


@app.get("/avatar")
async def get_random_avatar_endpoint(
    width: Optional[int] = Query(None, gt=0, le=4000, description="Desired width in pixels"),
    height: Optional[int] = Query(None, gt=0, le=4000, description="Desired height in pixels")
):
    """
    Get a random avatar from the avatars folder.

    Optionally resize the avatar by providing width and/or height parameters.
    If only one dimension is provided, aspect ratio is maintained.
    """
    avatar_path = get_random_avatar()

    try:
        with Image.open(avatar_path) as img:
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
                headers={"X-Avatar-Source": avatar_path.name}
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing avatar: {str(e)}")


@app.get("/tags")
async def list_tags():
    """
    List available metadata schema and statistics.

    Returns the schema of available tag values and counts of tagged images.
    """
    metadata = load_metadata()
    schema = metadata.get("schema", {})
    images_metadata = metadata.get("images", {})

    # Count images with each tag
    stats = {
        "total_images": len([
            f for f in MEDIA_FOLDER.iterdir()
            if f.is_file() and f.suffix.lower() in SUPPORTED_FORMATS
        ]) if MEDIA_FOLDER.exists() else 0,
        "tagged_images": len(images_metadata),
        "aircraft_counts": {},
        "location_counts": {},
        "time_of_day_counts": {},
        "weather_counts": {},
        "tag_counts": {}
    }

    # Count occurrences
    for image_meta in images_metadata.values():
        # Aircraft
        for aircraft in image_meta.get("aircraft", []):
            stats["aircraft_counts"][aircraft] = stats["aircraft_counts"].get(aircraft, 0) + 1

        # Location
        location = image_meta.get("location")
        if location:
            stats["location_counts"][location] = stats["location_counts"].get(location, 0) + 1

        # Time of day
        time_of_day = image_meta.get("time_of_day")
        if time_of_day:
            stats["time_of_day_counts"][time_of_day] = stats["time_of_day_counts"].get(time_of_day, 0) + 1

        # Weather
        weather = image_meta.get("weather")
        if weather:
            stats["weather_counts"][weather] = stats["weather_counts"].get(weather, 0) + 1

        # Tags
        for tag in image_meta.get("tags", []):
            stats["tag_counts"][tag] = stats["tag_counts"].get(tag, 0) + 1

    return {
        "schema": schema,
        "statistics": stats
    }


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
