#!/usr/bin/env python3
"""Generate metadata.json template for all images in the media folder."""

import json
from pathlib import Path

MEDIA_FOLDER = Path("media")
SUPPORTED_FORMATS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}

# Common DCS World aircraft that might appear in screenshots
AIRCRAFT_OPTIONS = [
    "F-18C", "F-16C", "F-15C", "F-15E", "F-14", "F-5E", "F-4E",
    "A-10C", "AV-8B", "JF-17", "Mirage-2000C", "AJS-37",
    "Mi-24", "AH-64D", "UH-60L", "OH-58D", "Ka-50", "Mi-8",
    "SA-342", "CH-47F"
]

LOCATION_OPTIONS = [
    "carrier", "desert", "mountains", "urban", "sea", "airfield",
    "forest", "snow", "island"
]

TIME_OF_DAY_OPTIONS = ["day", "night", "dawn", "dusk"]

WEATHER_OPTIONS = ["clear", "cloudy", "rain", "fog", "storm"]

TAG_OPTIONS = [
    "combat", "landing", "takeoff", "formation", "cockpit",
    "external", "weapon", "refueling", "carrier-ops", "ground-attack"
]

def generate_metadata():
    """Generate metadata template for all images."""

    # Get all image files
    image_files = sorted([
        f.name for f in MEDIA_FOLDER.iterdir()
        if f.is_file() and f.suffix.lower() in SUPPORTED_FORMATS
    ])

    # Create metadata structure
    metadata = {
        "schema": {
            "description": "Available values for each metadata field",
            "aircraft": AIRCRAFT_OPTIONS,
            "location": LOCATION_OPTIONS,
            "time_of_day": TIME_OF_DAY_OPTIONS,
            "weather": WEATHER_OPTIONS,
            "tags": TAG_OPTIONS
        },
        "images": {}
    }

    # Add empty template for each image
    for image_name in image_files:
        metadata["images"][image_name] = {
            "aircraft": [],
            "location": "",
            "time_of_day": "",
            "weather": "",
            "tags": []
        }

    # Write to file
    output_path = MEDIA_FOLDER / "metadata.json"
    with open(output_path, "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"Generated metadata template for {len(image_files)} images")
    print(f"Output: {output_path}")
    print(f"\nNext steps:")
    print(f"1. Edit {output_path} to add tags to your images")
    print(f"2. You can add multiple aircraft to the 'aircraft' array")
    print(f"3. Add custom tags to the 'tags' array")
    print(f"4. The API will filter images based on these metadata fields")

if __name__ == "__main__":
    generate_metadata()
