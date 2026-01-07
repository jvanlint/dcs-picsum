# Random Screenshot API

A lightweight FastAPI application that serves random images from a media folder with optional resizing capabilities.

## Features

- Serves random screenshots from the `media` folder
- **Metadata-based filtering** by aircraft, location, weather, time of day, and custom tags
- Optional image resizing via query parameters
- Maintains aspect ratio when only one dimension is specified
- Supports multiple image formats (JPG, PNG, GIF, BMP, WebP)
- Returns image metadata in response headers
- Ready for deployment on Railway

## Setup

### Local Development

1. Activate the virtual environment:
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Add your images to the `media` folder

4. Run the development server:
```bash
hypercorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

### GET /
Root endpoint with API information

### GET /random
Get a random screenshot from the media folder

**Query Parameters:**
- `width` (optional): Desired width in pixels (1-4000)
- `height` (optional): Desired height in pixels (1-4000)
- `aircraft` (optional): Filter by aircraft type (e.g., F-18C, A-10C)
- `location` (optional): Filter by location (e.g., carrier, desert)
- `time_of_day` (optional): Filter by time (day, night, dawn, dusk)
- `weather` (optional): Filter by weather (clear, cloudy, rain, fog)
- `tags` (optional): Filter by comma-separated tags (e.g., combat,landing)

**Examples:**
- `/random` - Get a random image at original size
- `/random?width=800` - Resize to 800px width, maintain aspect ratio
- `/random?aircraft=F-18C` - Get a random F-18C screenshot
- `/random?aircraft=F-18C&location=carrier` - F-18C on carrier
- `/random?aircraft=A-10C&width=800&height=600` - Resized A-10C image
- `/random?tags=combat,landing` - Images tagged with both combat and landing

**Response Headers:**
The API includes metadata in response headers:
- `X-Image-Source`: Filename of the returned image
- `X-Image-Aircraft`: Comma-separated aircraft types
- `X-Image-Location`: Location metadata
- `X-Image-TimeOfDay`: Time of day
- `X-Image-Weather`: Weather conditions
- `X-Image-Tags`: Comma-separated custom tags

### GET /tags
List available metadata schema and statistics

Returns the available values for each metadata field and counts of how many images have each tag.

### GET /health
Health check endpoint showing API status and image count

## Metadata Management

The API supports filtering images by metadata stored in `media/metadata.json`.

### Generating Metadata Template

To generate a metadata template for all your images:

```bash
python generate_metadata.py
```

This creates `media/metadata.json` with entries for all images. Edit this file to add metadata:

```json
{
  "images": {
    "my-screenshot.jpg": {
      "aircraft": ["F-18C", "F-14"],
      "location": "carrier",
      "time_of_day": "dawn",
      "weather": "clear",
      "tags": ["formation", "carrier-ops"]
    }
  },
  "schema": {
    "aircraft": ["F-18C", "F-16C", "A-10C", ...],
    "location": ["carrier", "desert", "mountains", ...],
    ...
  }
}
```

### Metadata Fields

- **aircraft**: Array of aircraft types in the screenshot
- **location**: Single location value (carrier, desert, etc.)
- **time_of_day**: Single value (day, night, dawn, dusk)
- **weather**: Single value (clear, cloudy, rain, fog, storm)
- **tags**: Array of custom tags (combat, landing, cockpit, etc.)

The `schema` section lists available values for reference.

## Deployment to Railway

1. Push your code to a GitHub repository
2. Connect your repository to Railway
3. Railway will automatically detect the configuration from `railway.json`
4. Add your images to the `media` folder before deploying, or use Railway volumes for persistent storage

## Project Structure

```
.
├── main.py                 # FastAPI application
├── generate_metadata.py    # Utility to generate metadata template
├── requirements.txt        # Python dependencies
├── railway.json            # Railway deployment configuration
├── media/                  # Folder for your screenshots
│   ├── metadata.json       # Image metadata for filtering
│   └── *.jpg/png/...       # Your image files
├── venv/                   # Virtual environment (not committed)
└── README.md              # This file
```
