# Random Screenshot API

A lightweight FastAPI application that serves random images from a media folder with optional resizing capabilities.

## Features

- Serves random screenshots from the `media` folder
- Optional image resizing via query parameters
- Maintains aspect ratio when only one dimension is specified
- Supports multiple image formats (JPG, PNG, GIF, BMP, WebP)
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

**Examples:**
- `/random` - Get a random image at original size
- `/random?width=800` - Resize to 800px width, maintain aspect ratio
- `/random?height=600` - Resize to 600px height, maintain aspect ratio
- `/random?width=800&height=600` - Resize to exact dimensions

### GET /health
Health check endpoint showing API status and image count

## Deployment to Railway

1. Push your code to a GitHub repository
2. Connect your repository to Railway
3. Railway will automatically detect the configuration from `railway.json`
4. Add your images to the `media` folder before deploying, or use Railway volumes for persistent storage

## Project Structure

```
.
├── main.py              # FastAPI application
├── requirements.txt     # Python dependencies
├── railway.json         # Railway deployment configuration
├── media/              # Folder for your screenshots
├── venv/               # Virtual environment (not committed)
└── README.md           # This file
```
