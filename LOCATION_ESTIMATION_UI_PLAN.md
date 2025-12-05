# Location-Based Estimation UI Plan

## Requirements
1. Two input methods:
   - **Method 1: Location/City** - User enters city/location (address optional)
   - **Method 2: Coordinates** - User enters latitude and longitude
2. Results must display correctly to allow moving to next step
3. If API fails, use random irradiance (4.8 to 5.5 for Pakistan)

## UI Design Plan

### Layout Structure
```
┌─────────────────────────────────────────┐
│  Step 1 of 4: Location Based Estimation │
├─────────────────────────────────────────┤
│                                         │
│  [Tab 1: Enter Location] [Tab 2: Enter Coordinates]
│                                         │
│  ┌───────────────────────────────────┐ │
│  │ Tab Content Area                  │ │
│  │                                   │ │
│  │ Form Fields                       │ │
│  │ [Calculate Button]                │ │
│  └───────────────────────────────────┘ │
│                                         │
│  OR (if results exist)                 │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │ Results Display                    │ │
│  │ - Location Info                    │ │
│  │ - Solar Irradiance                 │ │
│  │ - Source                           │ │
│  │ [Clear] [Next: Energy Consumption] │ │
│  └───────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

### Tab 1: Enter Location
**Required Fields:**
- City (required) - Text input
- State/Province (required) - Text input or dropdown

**Optional Fields:**
- Street Address (optional) - Text input

**Action:**
- Button: "Calculate Solar Potential"

**Process:**
1. User enters city and state
2. System geocodes to get coordinates
3. Calculates solar irradiance
4. Shows results

### Tab 2: Enter Coordinates
**Required Fields:**
- Latitude (required) - Number input (23.5 to 37.0)
- Longitude (required) - Number input (60.8 to 77.8)

**Optional Fields:**
- Address (optional) - Text input

**Action:**
- Button: "Calculate Solar Potential"

**Process:**
1. User enters latitude and longitude
2. Validates coordinates (Pakistan boundaries)
3. Reverse geocodes to get address (optional)
4. Calculates solar irradiance
5. Shows results

### Results Display
**Shows:**
- Address/Location
- City, State
- Coordinates (lat, lng)
- Solar Irradiance (kWh/m²/day)
- Source (API name or "Random")
- Confidence level

**Actions:**
- "Clear Results" button
- "Next: Energy Consumption" button (enabled when results exist)

## Implementation Steps

1. **Update View Logic:**
   - Simplify input validation (city+state OR lat+lng)
   - Ensure results always display
   - Add random fallback (4.8-5.5)

2. **Update Template:**
   - Clean tab interface
   - Make address optional
   - Ensure results display correctly

3. **Update Utils:**
   - Ensure random fallback works
   - Use Pakistan cities irradiance data if available

4. **Test:**
   - Test location input
   - Test coordinates input
   - Test API failure (random fallback)
   - Verify results display
   - Verify "Next" button works

