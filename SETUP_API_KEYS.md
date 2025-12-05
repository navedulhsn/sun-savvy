# API Keys Setup Guide

## Google Maps API Key Setup

### Step 1: Get Your API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Sign in with your Google account
3. Create a new project (or select existing one)
4. Enable these APIs:
   - **Maps JavaScript API**
   - **Geocoding API**
5. Go to "Credentials" → "Create Credentials" → "API Key"
6. Copy your API key

### Step 2: Add to .env File

1. Create a file named `.env` in the `sun-savvy` folder (same directory as `manage.py`)
2. Add this line:
   ```
   GOOGLE_MAPS_API_KEY=your_actual_api_key_here
   ```
3. Replace `your_actual_api_key_here` with your actual API key

### Step 3: Restart Server

Restart your Django development server:
```bash
python manage.py runserver
```

## Other Optional API Keys

You can also add these to your `.env` file:

```
# Google Gemini API (for AI location analysis)
GEMINI_API_KEY=your_gemini_key_here

# Solcast API (for solar irradiance data)
SOLCAST_API_KEY=your_solcast_key_here

# OpenWeatherMap API (backup for solar data)
OPENWEATHER_API_KEY=your_openweather_key_here
```

## Important Notes

- The `.env` file is in `.gitignore` for security (it won't be committed to git)
- Never share your API keys publicly
- Keep your `.env` file secure and don't commit it to version control

