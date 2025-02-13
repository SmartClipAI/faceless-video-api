# Faceless Video API

---
> ## 🎬 Special Offer from FacelessVideos.app!
> 
> ### Create Professional Faceless Videos with AI - In One Click!
>
> ✨ **One-stop automated video creation platform:**
> - 🤖 Generate complete faceless videos from just text input
> - 🎨 Choose between Flux Schnell and Flux Dev AI models
> - 🎁 **Limited Time**: New users get 1000 FREE credits!
>
> [🚀 Start Creating Now →](https://facelessvideos.app/)
---

## Project Overview

A FastAPI-based service that powers automated video content creation through AI. This API service streamlines the process of story generation, image creation, and video production by providing endpoints for generating stories, creating corresponding images, and compiling them into complete videos with subtitles.


## Features

### Story Generation
- Rich story type support:
  - Scary Stories
  - Mystery Tales
  - Bedtime Stories
  - Interesting History
  - Urban Legends
  - Motivational Stories
  - Fun Facts
  - Long Form Jokes
  - Life Pro Tips
  - Philosophy
  - Love Stories
  - Custom Topics

### Image Generation
- AI-powered image creation from story scenes
- Multiple style options:
  - Photorealistic
  - Cinematic
  - Anime
  - Comic-book
  - Pixar-art
- Consistent character appearance across scenes

### Video Production
- Automated video compilation with subtitles
- Multi-language support:
  - English, Chinese, French, German
  - Spanish, Japanese, Russian
  - And many more...
- Multiple voice options:
  - Echo, Alloy, Onyx
  - Fable, Nova, Shimmer
- Customizable video duration (short/long)

### System Features
- RESTful API endpoints
- Token-based authentication
- PostgreSQL database
- Async processing with background tasks
- Progress tracking and status updates
- Error handling and recovery
- API rate limiting and monitoring

## Environment Variables

Required environment variables in `.env`:
```bash
# OpenAI Configuration (Default)
OPENAI_BASE_URL="your-openai-base-url"
OPENAI_API_KEY="sk-***********************************"

# Azure OpenAI Configuration (Optional)
# AZURE_OPENAI_ENDPOINT="https://your-azure-openai-endpoint/"
# AZURE_OPENAI_API_KEY="your-azure-openai-key"
# Note: To use Azure OpenAI, set "use_azure_openai": true in config.json

# AI Service Keys (Choose one)
# Option 1: FAL (Default)
FAL_KEY="********-****-****-****-************:********************************"
# Option 2: Replicate (Alternative)
# REPLICATE_API_TOKEN="r8_********************************"
# Note: To use Replicate, set "use_fal_flux": false in config.json

# Database Configuration
DATABASE_URL="your-postgresql-database-url"

# JWT Secret Key
SECRET_KEY="your-secret-key"

# Admin User Configuration
ADMIN_USERNAME="admin"
ADMIN_EMAIL="admin@example.com"
ADMIN_PASSWORD="cNv4wL8KuP3o%"

# Storage Configuration (Cloudflare R2)
R2_BUCKET_NAME="faceless-dev-1-videos"
R2_ENDPOINT="https://{hash}.r2.cloudflarestorage.com"
R2_PUBLIC_ENDPOINT="https://pub-{hash}.r2.dev"
R2_ACCESS_KEY_ID="your-r2-access-key-id"
R2_SECRET_ACCESS_KEY="your-r2-secret-access-key"
```

## Requirements

- Python 3.8+
- PostgreSQL database

## Installation

1. Clone the repository
```bash
git clone https://github.com/SmartClipAI/faceless-video-api
cd faceless-video-api
```

2. Create and activate virtual environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Environment Configuration

Copy the environment template and configure the variables:
```bash
cp .env.example .env
```

## Database Setup

1. Ensure PostgreSQL is running

2. Create database
```bash
createdb faceless_db  # Using PostgreSQL CLI
```

3. Configure database connection
   Edit your `.env` file to set the database URL:
   ```bash
   DATABASE_URL=postgresql://username:password@localhost:5432/faceless_db
   ```
   Replace `username`, `password` with your PostgreSQL credentials.

4. Initialize database tables
```bash
python -m app.scripts.run_init_db
```

⚠️ **WARNING**: The database initialization command will:
- Drop all existing tables
- Delete all data in the database
- Recreate all tables from scratch
- Create a default admin user

You will be prompted for confirmation before the operation proceeds.

## Running the Service

### Development
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Documentation

After starting the service, access the API documentation at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Swagger Authorization Setup

To use the API endpoints in Swagger UI, you need to authenticate first:


1. Click the green "Authorize" button at the top right corner of the Swagger UI
![Swagger Auth Token](assets/auth1.png)
2. In the auth section, you'll find "OAuth2PasswordBearer" authentication:
   - Username: Use your admin username (default: `admin`)
   - Password: Use your admin password (from `.env` file)
   - Leave other fields empty
![Swagger Auth Dialog](assets/auth2.png)
3. Click "Authorize" to save your credentials
4. Now you can access all protected endpoints


Alternatively, you can get a token directly using the `/v1/auth/token` endpoint:
1. Expand the `/v1/auth/token` POST endpoint
2. Set the following required fields:
   - grant_type: `password`
   - username: your admin username
   - password: your admin password
3. Execute the request to receive your access token

For detailed API documentation, see [docs/api.md](docs/api.md)

## License

[MIT License](LICENSE)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Submit a Pull Request

## Support

For issues and questions, please create a GitHub Issue.

### Configuration Settings

The `config.json` file contains important settings for controlling the application behavior:

```json
{
    "story_limit_short": {
      "char_limit_min": 700,    // Minimum characters for short stories
      "char_limit_max": 800     // Maximum characters for short stories
    },
    "story_limit_long": {
      "char_limit_min": 900,    // Minimum characters for long stories
      "char_limit_max": 1000    // Maximum characters for long stories
    },
    "storyboard": {
      "max_scenes": 14          // Maximum number of scenes per story
    },
    "openai": {
      "model": "gpt-4",         // OpenAI model for story generation
      "temperature": 0.9        // Creativity level (0.0-1.0)
    },
    "replicate_flux_api": {
      "model": "black-forest-labs/flux-dev",
      "aspect_ratio": "9:16",   // Video aspect ratio
      "num_inference_steps": 28,
      "guidance": 3.5,
      "output_quality": 100
    },
    "fal_flux_dev_api": {
      "model": "fal-ai/flux/dev",
      "image_size": "portrait_16_9",
      "num_inference_steps": 28,
      "guidance_scale": 3.5,
      "enable_safety_checker": false,
      "num_images": 1
    },
    "fal_flux_schnell_api": {
      "model": "fal-ai/flux/schnell",
      "image_size": "portrait_16_9",
      "guidance_scale": 3.5,
      "enable_safety_checker": false,
      "num_images": 1
    },
    "tts": {
      "speech_rate": 1.1        // Text-to-speech rate
    },
    "use_azure_openai": false,  // Whether to use Azure OpenAI
    "use_fal_flux": true,       // Use FAL (true) or Replicate (false)
    "use_fal_flux_dev": false   // Use FAL dev model instead of schnell
}
```

#### Key Configuration Sections:

1. **Story Limits**
   - `story_limit_short`: Character limits for short stories
   - `story_limit_long`: Character limits for long stories
   - `storyboard.max_scenes`: Maximum number of scenes per story

2. **OpenAI Settings**
   - Model configuration for story generation
   - Temperature controls creativity level

3. **Image Generation**
   - **FAL Settings** (Default):
     - Two model options: schnell (fast) or dev (development)
     - Portrait 16:9 aspect ratio
     - Configurable inference parameters
   
   - **Replicate Settings** (Alternative):
     - Uses black-forest-labs/flux-dev model
     - 9:16 aspect ratio for vertical videos
     - Quality and guidance settings

4. **Feature Toggles**
   - `use_fal_flux`: Switch between FAL and Replicate
   - `use_fal_flux_dev`: Toggle between FAL models
   - `use_azure_openai`: OpenAI API endpoint selection

5. **Text-to-Speech**
   - Speech rate configuration for video narration


## Supported Fonts

![Available Font Styles](assets/font.png)

The application supports the following font styles for text rendering:

- Titan One
- Ranchers
- Rampart One
- Permanent Marker
- Open Sans
- Noto Sans
- Montserrat
- Luckiest Guy
- Knewave
- Jua
- Creepster
- Caveat
- Bungee
- Bebas Neue
- Bangers
- Bakbak One

These fonts can be used for customizing the text appearance in generated videos and images.