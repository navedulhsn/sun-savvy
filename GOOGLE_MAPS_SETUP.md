# Google Maps API Setup Guide

This guide will help you set up Google Maps API for the location-based solar estimation feature.

## Step 1: Get a Google Cloud Account

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Sign in with your Google account
3. Create a new project (or select an existing one)
   - Click on the project dropdown at the top
   - Click "New Project"
   - Enter a project name (e.g., "SunSavvy")
   - Click "Create"

## Step 2: Enable Google Maps JavaScript API

1. In the Google Cloud Console, go to **APIs & Services** > **Library**
2. Search for "Maps JavaScript API"
3. Click on "Maps JavaScript API"
4. Click the **Enable** button

## Step 3: Enable Geocoding API (for address lookup)

1. Still in the **APIs & Services** > **Library**
2. Search for "Geocoding API"
3. Click on "Geocoding API"
4. Click the **Enable** button

## Step 4: Create API Key

1. Go to **APIs & Services** > **Credentials**
2. Click **Create Credentials** > **API Key**
3. A popup will show your API key - **Copy it** (you'll need it in the next step)
4. (Optional) Click **Restrict Key** to add restrictions:
   - Under "Application restrictions", select "HTTP referrers"
   - Add your website URLs (e.g., `http://127.0.0.1:8000/*`, `http://localhost:8000/*`)
   - Under "API restrictions", select "Restrict key"
   - Select "Maps JavaScript API" and "Geocoding API"
   - Click "Save"

## Step 5: Add API Key to Your Project

### Option A: Using .env file (Recommended)

1. Create a `.env` file in your project root directory (if it doesn't exist)
2. Add the following line:
   ```
   GOOGLE_MAPS_API_KEY=your-api-key-here
   ```
   Replace `your-api-key-here` with the API key you copied in Step 4.

3. Make sure `.env` is in your `.gitignore` file (to keep your API key secret)

### Option B: Set Environment Variable (Windows)

1. Open PowerShell or Command Prompt
2. Set the environment variable:
   ```powershell
   $env:GOOGLE_MAPS_API_KEY="your-api-key-here"
   ```
   (This only works for the current session)

   For permanent setup:
   - Open System Properties > Environment Variables
   - Add new User variable:
     - Variable name: `GOOGLE_MAPS_API_KEY`
     - Variable value: `your-api-key-here`

### Option C: Set Environment Variable (Linux/Mac)

```bash
export GOOGLE_MAPS_API_KEY="your-api-key-here"
```

For permanent setup, add to `~/.bashrc` or `~/.zshrc`:
```bash
echo 'export GOOGLE_MAPS_API_KEY="your-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

## Step 6: Restart Your Django Server

After adding the API key, restart your Django development server:

```bash
# Stop the server (Ctrl+C)
# Then restart:
python manage.py runserver
```

## Step 7: Test the Map

1. Go to the Solar Estimation page
2. Select "Select on Map" option
3. You should see an interactive Google Map
4. Click anywhere on the map to select a location
5. The address and coordinates should auto-fill

## Troubleshooting

### Map still shows warning message

1. **Check if API key is loaded:**
   - Make sure `.env` file is in the project root (same level as `manage.py`)
   - Restart the Django server after adding the key
   - Check for typos in the API key

2. **Check API key restrictions:**
   - If you restricted the key, make sure `http://127.0.0.1:8000/*` is in the allowed referrers
   - Make sure "Maps JavaScript API" and "Geocoding API" are enabled

3. **Check billing:**
   - Google Maps API requires a billing account (but has free tier)
   - Go to **Billing** in Google Cloud Console
   - Link a billing account (credit card required, but you get $200 free credit monthly)

### "This API project is not authorized to use this API"

- Make sure you enabled both "Maps JavaScript API" and "Geocoding API" in Step 2-3

### Map loads but clicking doesn't work

- Check browser console for errors (F12)
- Make sure Geocoding API is enabled

## Free Tier Limits

Google Maps API provides:
- **$200 free credit per month**
- This covers approximately:
  - 28,000 map loads
  - 40,000 geocoding requests

For development and small projects, this is usually sufficient.

## Security Notes

⚠️ **Important:**
- Never commit your `.env` file to Git
- Never share your API key publicly
- Use API key restrictions in production
- Monitor your API usage in Google Cloud Console

## Need Help?

- [Google Maps API Documentation](https://developers.google.com/maps/documentation/javascript)
- [Google Cloud Console](https://console.cloud.google.com/)
- [API Key Best Practices](https://developers.google.com/maps/api-security-best-practices)

