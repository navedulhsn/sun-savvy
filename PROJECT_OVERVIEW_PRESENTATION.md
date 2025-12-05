# SunSavvy Project - Complete Overview for Presentation

## 📋 PROJECT STRUCTURE

### **1. WHERE PAGE CODE IS WRITTEN**

#### **Frontend Templates (HTML Pages)**
- **Location**: `templates/solar/` folder
- **Total Pages**: 38 HTML template files
- **Main Pages**:
  - `home.html` - Landing page
  - `dashboard.html` - User dashboard
  - `login.html` - Login page
  - `register.html` - Registration selection
  - `solar_estimation.html` - Main estimation page
  - `estimation_location.html` - Location-based estimation
  - `estimation_energy.html` - Energy consumption calculation
  - `estimation_roof.html` - Roof area calculation
  - `estimation_savings.html` - Savings & ROI calculation
  - `fault_detection.html` - AI fault detection upload
  - `fault_detection_result.html` - Fault detection results
  - `fault_detection_history.html` - Fault detection history
  - `service_providers.html` - List of service providers
  - `provider_dashboard.html` - Service provider dashboard
  - `admin_dashboard.html` - Admin dashboard
  - And many more...

#### **Backend Views (Python Logic)**
- **Location**: `solar/views/` folder
- **View Files**:
  - `customer_views.py` - All customer/user functionality (estimation, dashboard, history)
  - `provider_views.py` - Service provider functionality
  - `admin_views.py` - Admin panel functionality
  - `ai_views.py` - AI fault detection and chatbot
  - `auth_views.py` - Login, registration, authentication
  - `common_views.py` - Shared/common functionality

#### **Base Template**
- **Location**: `templates/base.html`
- **Purpose**: Main template that all pages extend from
- **Contains**: Navigation bar, footer, Bootstrap CSS/JS, common structure

---

### **2. DATABASE (SQLite)**

#### **Database File Location**
- **File**: `db.sqlite3` (in project root)
- **Type**: SQLite3 (lightweight, file-based database)
- **Configuration**: Set in `sunsavvy/settings.py` line 84-88

#### **Database Models (Tables)**
- **Location**: `solar/models/` folder
- **Model Files**:
  1. **`users.py`** - User profiles, service providers, authorized persons
  2. **`estimation.py`** - Solar estimations, appliances
  3. **`fault_detection.py`** - Fault detection records
  4. **`requests.py`** - Service requests
  5. **`products.py`** - Provider panels/products

#### **Main Database Tables**:
1. **SolarEstimation** - Stores all solar estimation calculations
   - Fields: latitude, longitude, address, city, state, monthly consumption, rooftop area, panels needed, costs, savings, ROI, etc.

2. **FaultDetection** - Stores AI fault detection results
   - Fields: user, image, fault_type, confidence_score, description, detection_result (JSON)

3. **ServiceProvider** - Service provider information
   - Fields: company name, contact info, services, pricing

4. **ServiceRequest** - Customer requests to providers
   - Fields: user, provider, service type, status, dates

5. **Appliance** - Household appliances for energy calculation
   - Fields: name, power rating, category

6. **ProviderPanel** - Solar panels offered by providers
   - Fields: name, capacity, price, specifications

7. **UserProfile** - Extended user information
   - Fields: phone, address, user type

#### **Database Migrations**
- **Location**: `solar/migrations/` folder
- **Purpose**: Tracks database schema changes
- **Files**: 9 migration files showing database evolution

---

### **3. APIs USED**

#### **Location-Based APIs (Free)**
1. **OpenStreetMap Nominatim API** (PRIMARY - FREE)
   - **Purpose**: Convert addresses to coordinates (geocoding)
   - **Purpose**: Convert coordinates to addresses (reverse geocoding)
   - **Location in Code**: `solar/utils.py` - `geocode_address()` and `reverse_geocode()` functions
   - **No API Key Required**: Completely free
   - **Rate Limit**: 1 request per second

2. **Google Maps Geocoding API** (FALLBACK - PAID)
   - **Purpose**: Backup geocoding if OpenStreetMap fails
   - **Location in Code**: `solar/utils.py` - `geocode_address()` function
   - **Requires API Key**: Set in settings as `GOOGLE_MAPS_API_KEY`

#### **Solar Irradiance APIs (Weather Data)**
1. **NASA POWER API** (PRIMARY - FREE)
   - **Purpose**: Get historical solar irradiance data
   - **Location in Code**: `solar/utils.py` - `get_solar_irradiance_nasa_power()` function
   - **No API Key Required**: Completely free
   - **URL**: `https://power.larc.nasa.gov/api/temporal/daily/point`

2. **Solcast API** (OPTIONAL - PAID)
   - **Purpose**: Get accurate solar radiation forecasts
   - **Location in Code**: `solar/utils.py` - `get_solar_irradiance()` function
   - **Requires API Key**: Set in settings as `SOLCAST_API_KEY`
   - **Priority**: Tried first if key is available

3. **OpenWeatherMap API** (FALLBACK - PAID)
   - **Purpose**: Get current weather to estimate solar irradiance
   - **Location in Code**: `solar/utils.py` - `get_solar_irradiance()` function
   - **Requires API Key**: Set in settings as `OPENWEATHER_API_KEY`
   - **URL**: `https://api.openweathermap.org/data/2.5/weather`

#### **AI APIs**
1. **Google Gemini API** (OPTIONAL - PAID)
   - **Purpose**: AI-powered location analysis and insights
   - **Location in Code**: `solar/utils.py` - `analyze_location_with_gemini()` function
   - **Requires API Key**: Set in settings as `GEMINI_API_KEY`
   - **Has Fallback**: Works without API key (basic analysis)

2. **Hugging Face Mistral AI** (Chatbot)
   - **Purpose**: AI chatbot for solar questions
   - **Location in Code**: `solar/views/ai_views.py` - `chatbot()` function
   - **Model**: `mistralai/Mistral-7B-Instruct-v0.2`
   - **Requires Token**: Set as `HF_TOKEN` environment variable

#### **API Priority Order (Solar Irradiance)**
1. Solcast API (if key available) - Most accurate
2. NASA POWER API (always tried) - Free and reliable
3. OpenWeatherMap API (if key available) - Current weather-based
4. Random fallback (4.8-5.8 kWh/m²/day) - Pakistan average if all APIs fail

---

### **4. STYLING (CSS & Design)**

#### **CSS Framework**
- **Bootstrap 5.3.0** (CDN)
  - **Location**: Loaded in `templates/base.html`
  - **URL**: `https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css`
  - **Purpose**: Responsive grid system, components, utilities

#### **Icons**
- **Bootstrap Icons** (CDN)
  - **Location**: Loaded in `templates/base.html`
  - **URL**: `https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css`
  - **Purpose**: Icon library for UI elements

#### **Fonts**
- **Google Fonts - Inter** (CDN)
  - **Location**: Loaded in `templates/base.html`
  - **URL**: `https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap`
  - **Purpose**: Modern, clean typography

#### **Custom CSS**
- **Location**: `static/css/style.css`
- **Features**:
  - Glassmorphism effects (blur, transparency)
  - Custom navbar styling
  - Button hover effects
  - Color schemes
  - Responsive design adjustments

#### **Inline Styles**
- **Location**: Individual template files (`.html` files)
- **Purpose**: Page-specific styling
- **Example**: Apple-inspired design in estimation pages

#### **Design Style**
- **Theme**: Modern, clean, Apple-inspired design
- **Colors**: Primary blue (#0d6efd), success green, warning yellow, danger red
- **Effects**: Glassmorphism (blur effects), shadows, hover animations
- **Layout**: Card-based, responsive grid system

---

### **5. AI/ML FEATURES**

#### **Fault Detection AI Model**
- **Location**: `ai_models/physical_fault_detection_vgg16_finetuned.h5`
- **Type**: TensorFlow/Keras VGG16 model (fine-tuned)
- **Purpose**: Detect solar panel faults from images
- **Fault Types Detected**:
  - Clean (no issues)
  - Dusty
  - Bird-drop
  - Physical-Damage
  - Electrical-damage
  - Snow-Covered
- **Fallback**: Basic image analysis if TensorFlow not available
- **Code Location**: `solar/utils.py` - `detect_fault_ai()` function

#### **Dependencies**
- **TensorFlow 2.20.0** (for AI model)
- **Pillow** (image processing)
- **NumPy** (array operations)

---

### **6. PROJECT ARCHITECTURE**

#### **Framework**
- **Django 5.2.8** (Python web framework)
- **MVC Pattern**: Models (database), Views (logic), Templates (UI)

#### **File Structure**
```
sun-savvy/
├── sunsavvy/          # Main Django project settings
│   ├── settings.py    # Configuration (database, APIs, etc.)
│   ├── urls.py        # Main URL routing
│   └── wsgi.py        # Web server interface
├── solar/              # Main application
│   ├── models/         # Database models
│   ├── views/          # View functions (business logic)
│   ├── templates/      # HTML templates
│   ├── utils.py        # Utility functions (APIs, calculations)
│   └── urls.py         # Application URL routing
├── templates/          # Base templates
├── static/             # CSS, JavaScript, images
├── media/              # User-uploaded files
├── ai_models/          # AI model files
└── db.sqlite3          # SQLite database
```

#### **URL Routing**
- **Main URLs**: `sunsavvy/urls.py` - Routes to different apps
- **App URLs**: `solar/urls.py` - Routes to specific views
- **Total Routes**: 30+ URL patterns

---

### **7. KEY FEATURES**

#### **Solar Estimation System**
1. **Location Module**: Enter address or coordinates, get solar irradiance
2. **Energy Module**: Calculate monthly energy consumption from appliances
3. **Roof Module**: Calculate rooftop area and panel capacity options
4. **Savings Module**: Calculate costs, savings, ROI, payback period

#### **Fault Detection**
- Upload solar panel image
- AI analyzes for faults
- Shows confidence score and recommendations
- History tracking

#### **Service Provider System**
- Providers can register and list services
- Customers can request services
- Request management system

#### **User Management**
- Three user types: Regular users, Service providers, Admins
- Email verification
- Separate dashboards for each type

---

### **8. TECHNOLOGIES & LIBRARIES**

#### **Backend**
- Django 5.2.8
- Python 3.x
- SQLite3 database
- Django Jazzmin (admin interface)

#### **Frontend**
- Bootstrap 5.3.0
- Bootstrap Icons
- Google Fonts (Inter)
- Custom CSS
- JavaScript (for dynamic features)

#### **APIs & External Services**
- OpenStreetMap Nominatim (free geocoding)
- NASA POWER (free solar data)
- Google Maps (optional geocoding)
- Solcast (optional solar forecasts)
- OpenWeatherMap (optional weather)
- Google Gemini (optional AI analysis)
- Hugging Face (AI chatbot)

#### **AI/ML**
- TensorFlow 2.20.0
- Keras (for model loading)
- Pillow (image processing)
- NumPy (numerical operations)

#### **Other Libraries**
- Requests (HTTP requests to APIs)
- Python-decouple (environment variables)
- Django dotenv (environment variables)

---

### **9. CONFIGURATION**

#### **Settings File**
- **Location**: `sunsavvy/settings.py`
- **Contains**:
  - Database configuration
  - API keys (from environment variables)
  - Email settings
  - Static/media file paths
  - Security settings

#### **Environment Variables**
- **File**: `.env` (in project root, not in repository)
- **Variables**:
  - `OPENWEATHER_API_KEY`
  - `SOLCAST_API_KEY`
  - `GOOGLE_MAPS_API_KEY`
  - `GEMINI_API_KEY`
  - `HF_TOKEN`
  - `EMAIL_HOST_USER`
  - `EMAIL_HOST_PASSWORD`

---

### **10. DATA FLOW**

#### **Solar Estimation Flow**
1. User enters location → Geocoding API gets coordinates
2. Coordinates → Solar irradiance APIs get sun data
3. User enters appliances → Calculate energy consumption
4. User enters roof size → Calculate panel options
5. All data → Calculate costs, savings, ROI
6. Results saved to database

#### **Fault Detection Flow**
1. User uploads image → Saved to media folder
2. Image → AI model analyzes
3. AI result → Stored in database
4. Result displayed to user

---

### **11. SECURITY FEATURES**

- User authentication (login/logout)
- Email verification
- CSRF protection
- Password validation
- Session management
- User role separation (customer/provider/admin)

---

### **12. DEPLOYMENT READY**

- Static files collection ready
- Media files handling
- Environment variable configuration
- Database migrations system
- Error handling and fallbacks

---

## 📊 SUMMARY FOR PRESENTATION

**Project Name**: SunSavvy - Solar Energy Estimation & Fault Detection Platform

**Technology Stack**:
- Backend: Django (Python)
- Database: SQLite3
- Frontend: Bootstrap 5, Custom CSS
- APIs: OpenStreetMap, NASA POWER, Google Maps, Solcast, OpenWeatherMap, Gemini AI
- AI: TensorFlow/Keras VGG16 model for fault detection

**Key Features**:
- 4-step solar estimation system
- AI-powered fault detection
- Service provider marketplace
- Multi-user system (customers, providers, admins)
- Real-time API integrations
- Historical data tracking

**Total Files**:
- 38 HTML templates
- 6 Python view files
- 5 Model files
- 1 Utility file (APIs & calculations)
- 1 Database file (SQLite)

**APIs Used**: 6 different APIs (3 free, 3 paid/optional)

---

**Good luck with your presentation!** 🎉

