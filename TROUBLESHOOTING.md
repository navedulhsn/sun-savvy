# 🔧 Solar Estimation Troubleshooting Guide

## Common Issues and Solutions

### Issue 1: Calculations Not Showing Results

**Symptoms:**
- Click "Calculate" button
- Page redirects but no results appear
- Modules remain in "not completed" state

**Solutions:**

1. **Check Browser Console for Errors**
   - Press F12 to open Developer Tools
   - Look for JavaScript errors
   - Look for failed network requests

2. **Check Django Server Logs**
   - Look for Python errors in terminal
   - Check for missing imports
   - Check for database errors

3. **Verify Session is Working**
   - Check if cookies are enabled
   - Try in incognito mode
   - Clear browser cache

### Issue 2: Database Save Errors

**Symptoms:**
- Message: "Analysis completed but not saved"
- Estimations not appearing in dashboard

**Required Fields Check:**
```python
# SolarEstimation model requires:
- user (ForeignKey)
- latitude, longitude (Decimal)
- address, city, state (CharField)
- monthly_consumption_kwh (Decimal)
- rooftop_length, rooftop_width, rooftop_area (Decimal)
- solar_irradiance (Decimal)
- panels_needed (Integer)
- panel_capacity_kw (Decimal)
- estimated_cost, annual_savings (Decimal)
- payback_period_years, roi_percentage (Decimal)
- annual_energy_generated (Decimal)
```

### Issue 3: Empty Dashboard

**Symptoms:**
- Dashboard shows "No estimations yet"
- But estimations were completed

**Check:**
1. Are you logged in as the same user?
2. Check database: `python manage.py dbshell` then `SELECT * FROM solar_solarestimation;`
3. Check if estimations are saved: Go to `/estimation/history/`

### Testing Steps:

#### Module 1: Location
1. Select "Google Map" or "Manual Input"
2. If Google Map: Click on map to select location
3. Fill in Address, City, State
4. Click "Calculate Solar Potential"
5. **Expected**: Green checkmark, results box appears
6. **Check**: `location_result` in session

#### Module 2: Energy
1. Select appliances
2. Set quantity and hours per day
3. Click "Calculate Energy Consumption"
4. **Expected**: Green checkmark, consumption results
5. **Check**: `energy_result` in session

#### Module 3: Roof
1. Enter roof length and width in meters
2. Click "Calculate Roof Area"
3. **Expected**: Green checkmark, panel options appear
4. **Check**: `roof_result` in session

#### Module 4: Savings & ROI
1. Select a panel option
2. Optionally enter electricity rate
3. Click "Calculate Savings & ROI"
4. **Expected**: Green checkmark, financial results, saved to database
5. **Check**: Database has new record

### Debug Commands:

```bash
# Check if server is running
python manage.py runserver

# Check for errors
python manage.py check

# Test database connection
python manage.py dbshell

# View all estimations
SELECT * FROM solar_solarestimation ORDER BY created_at DESC LIMIT 5;

# Count estimations per user
SELECT user_id, COUNT(*) FROM solar_solarestimation GROUP BY user_id;
```

### Quick Fixes:

#### Fix 1: Clear Session Data
```python
# In Django shell (python manage.py shell)
from django.contrib.sessions.models import Session
Session.objects.all().delete()
```

#### Fix 2: Check Appliances Exist
```python
# In Django shell
from solar.models import Appliance
print(Appliance.objects.count())
# Should be > 0
```

#### Fix 3: Test Utils Functions
```python
# In Django shell
from solar.utils import get_solar_irradiance, calculate_panel_capacity_options
irr = get_solar_irradiance(24.8607, 67.0011)
print(f"Irradiance: {irr}")

options = calculate_panel_capacity_options(100)  # 100 sqm roof
print(f"Panel options: {len(options)}")
```

### Expected Behavior:

1. **After Location Calculation:**
   - Results box appears with:
     - Address
     - City, State
     - Solar Irradiance (kWh/m²/day)
     - Coordinates
   - "Clear Results" button appears

2. **After Energy Calculation:**
   - Results box shows:
     - Total Monthly Consumption
     - Estimated Annual
     - Appliances Selected
     - Appliance Breakdown table

3. **After Roof Calculation:**
   - Results box shows:
     - Dimensions
     - Total Area
     - Available Panel Options (cards)

4. **After Savings Calculation:**
   - Results box shows:
     - System Capacity
     - Panels Needed
     - Total Cost
     - Annual Savings
     - Payback Period
     - ROI
   - Estimation saved to database
   - Appears in dashboard

### Common Errors:

**Error: "Please complete all previous modules first"**
- Solution: Complete modules 1, 2, and 3 before module 4

**Error: "Please select at least one appliance with usage hours"**
- Solution: Check appliances AND set hours > 0

**Error: "Please enter valid roof dimensions"**
- Solution: Enter positive numbers for length and width

**Error: Analysis completed but not saved**
- Check server logs for specific error
- Verify all required fields are in session
- Check database constraints

### Verification Checklist:

- [ ] Server is running without errors
- [ ] User is logged in
- [ ] Appliances exist in database
- [ ] Session cookies are enabled
- [ ] No JavaScript errors in console
- [ ] All form fields are filled correctly
- [ ] Results appear after each calculation
- [ ] Green checkmarks appear on completed modules
- [ ] Final estimation appears in dashboard
- [ ] Estimation appears in history page

---

**If issues persist:**
1. Check server terminal for Python errors
2. Check browser console for JavaScript errors
3. Try in a different browser
4. Clear all cookies and cache
5. Restart the Django server
