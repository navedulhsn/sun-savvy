# Plan: Free Location-Based Estimation (No Paid API Keys Required)

## Current Issues
- Google Maps API requires paid subscription after free tier
- Need free alternatives for geocoding and location services

## Solution: Use Free APIs and Manual Input

### Priority 1: Free Geocoding APIs (No Key Required)

#### Option A: OpenStreetMap Nominatim API (FREE, No Key)
- **Completely free** - No API key required
- **Rate limit**: 1 request per second (sufficient for our use)
- **Features**: 
  - Address to coordinates (geocoding)
  - Coordinates to address (reverse geocoding)
  - Works worldwide including Pakistan
- **Endpoint**: `https://nominatim.openstreetmap.org/search`
- **Reverse**: `https://nominatim.openstreetmap.org/reverse`

#### Option B: MapBox (Free Tier - 100,000 requests/month)
- Free tier available
- Requires API key but free
- Better rate limits than Nominatim

#### Option C: OpenCage Geocoding (Free Tier - 2,500 requests/day)
- Free tier available
- Requires API key but free
- Good for Pakistan

### Priority 2: Manual Coordinate Input (Always Available)
- Users can directly enter latitude/longitude
- No API needed
- Validate coordinates for Pakistan boundaries
- Show location on map using free map tiles (OpenStreetMap)

### Priority 3: Free Map Display
- Use Leaflet.js with OpenStreetMap tiles (completely free)
- No API key required
- Interactive maps with markers
- Works offline with cached tiles

## Implementation Plan

### Step 1: Replace Google Geocoding with OpenStreetMap Nominatim
- Update `geocode_address()` to use Nominatim API
- Update `reverse_geocode()` to use Nominatim API
- Add rate limiting (1 request per second)
- Add error handling and fallbacks

### Step 2: Replace Google Maps with Leaflet.js + OpenStreetMap
- Remove Google Maps JavaScript API dependency
- Integrate Leaflet.js (free, open-source)
- Use OpenStreetMap tiles (free)
- Add interactive map for coordinate input
- Show location preview

### Step 3: Enhance Manual Coordinate Input
- Add coordinate validation
- Add Pakistan boundary checking
- Add helpful hints and examples
- Add map preview using free tiles

### Step 4: Keep Address Input Working
- Use Nominatim for address geocoding
- Show user-friendly error messages
- Provide fallback to manual input

### Step 5: Remove Google Maps Dependency
- Make Google Maps optional (only if key is provided)
- Use free alternatives by default
- Keep code backward compatible

## Benefits
✅ **Completely free** - No paid API keys needed
✅ **No rate limit issues** - OpenStreetMap is generous
✅ **Works offline** - Can cache map tiles
✅ **Privacy-friendly** - OpenStreetMap doesn't track users
✅ **Always available** - Manual coordinate input always works

## Technical Details

### OpenStreetMap Nominatim API Usage

**Geocoding (Address → Coordinates):**
```
GET https://nominatim.openstreetmap.org/search?
    q={address}, {city}, {state}, Pakistan
    &format=json
    &limit=1
    &countrycodes=pk
```

**Reverse Geocoding (Coordinates → Address):**
```
GET https://nominatim.openstreetmap.org/reverse?
    lat={latitude}
    &lon={longitude}
    &format=json
```

### Leaflet.js Integration
- CDN: `https://unpkg.com/leaflet@1.9.4/dist/leaflet.js`
- Free map tiles: OpenStreetMap, CartoDB, etc.
- No API key required
- Full interactive map features

## Implementation Steps

1. ✅ Update `geocode_address()` to use Nominatim
2. ✅ Update `reverse_geocode()` to use Nominatim  
3. ✅ Replace Google Maps with Leaflet.js in template
4. ✅ Add rate limiting for Nominatim requests
5. ✅ Update coordinate validation
6. ✅ Test with Pakistani addresses
7. ✅ Make Google Maps optional (fallback only)

