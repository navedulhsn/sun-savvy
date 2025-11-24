# SunSavvy - Solar Estimator and ROI Calculator

A comprehensive web-based platform for solar energy estimation, ROI calculation, AI-powered fault detection, and service provider connections.

## Features

### Core Functionality
- **User Management**: Registration and authentication for end users and service providers
- **Location-Based Solar Estimation**: Real-time solar potential calculation using weather APIs
- **Energy Consumption Analysis**: Calculate solar needs based on monthly electricity usage
- **Rooftop Area Calculation**: Determine optimal panel placement based on roof dimensions
- **Financial Analysis**: ROI, payback period, and savings calculations
- **Solar Panel Recommendations**: Personalized recommendations based on location and needs

### Advanced Features
- **AI-Powered Fault Detection**: CNN-based image analysis for detecting physical faults in solar panels
- **AI Chatbot**: Intelligent assistant for user guidance and support
- **Service Provider Module**: Connect with verified local installers and repair services
- **Visual Dashboard**: Interactive charts and graphs for better understanding
- **Estimation History**: Track all your solar estimations over time

## Technology Stack

- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript
- **Backend**: Python 3.x, Django 4.2
- **Database**: SQLite (development) / MySQL (production)
- **AI/ML**: TensorFlow/Keras (for fault detection), OpenAI API (for chatbot)
- **APIs**: OpenWeather API, Solcast API, Google Maps API

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Setup Steps

1. **Clone or navigate to the project directory**
   ```bash
   cd FYP-SunSavy
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables** (Optional but recommended)
   Create a `.env` file in the project root:
   ```
   OPENWEATHER_API_KEY=your_openweather_api_key
   SOLCAST_API_KEY=your_solcast_api_key
   GOOGLE_MAPS_API_KEY=your_google_maps_api_key
   OPENAI_API_KEY=your_openai_api_key
   SECRET_KEY=your_django_secret_key
   ```

6. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

7. **Create a superuser** (for admin access)
   ```bash
   python manage.py createsuperuser
   ```

8. **Collect static files**
   ```bash
   python manage.py collectstatic
   ```

9. **Run the development server**
   ```bash
   python manage.py runserver
   ```

10. **Access the application**
    - Open your browser and go to: `http://127.0.0.1:8000/`
    - Admin panel: `http://127.0.0.1:8000/admin/`

## Project Structure

```
FYP-SunSavy/
├── sunsavvy/          # Main Django project settings
│   ├── settings.py    # Django configuration
│   ├── urls.py        # Main URL routing
│   └── wsgi.py        # WSGI configuration
├── solar/             # Main application
│   ├── models.py      # Database models
│   ├── views.py       # View functions
│   ├── urls.py        # App URL routing
│   ├── forms.py       # Django forms
│   ├── admin.py       # Admin configuration
│   └── utils.py       # Utility functions (calculations, API calls)
├── templates/         # HTML templates
│   ├── base.html      # Base template
│   └── solar/         # App-specific templates
├── static/            # Static files (CSS, JS, images)
│   ├── css/
│   └── js/
├── media/             # User-uploaded files
├── requirements.txt    # Python dependencies
└── manage.py          # Django management script
```

## Usage

### For End Users

1. **Register/Login**: Create an account or login
2. **Solar Estimation**: 
   - Go to "Solar Calculator"
   - Enter your location (latitude/longitude or address)
   - Input monthly electricity consumption
   - Enter rooftop dimensions
   - View detailed results including ROI and savings
3. **Fault Detection**: Upload solar panel images for AI analysis
4. **Service Providers**: Browse and contact verified service providers
5. **Dashboard**: View all your estimations and history

### For Service Providers

1. **Register**: Select "Register as Provider" and fill in company details
2. **Wait for Verification**: Admin will verify your account
3. **Receive Requests**: Users can contact you through the platform
4. **Manage Services**: Respond to service requests and quotes

## API Integration

The application integrates with several external APIs:

- **OpenWeather API**: For weather and solar irradiance data
- **Solcast API**: For accurate solar irradiance forecasts
- **Google Maps API**: For location services (optional)
- **OpenAI API**: For chatbot functionality (optional)

**Note**: API keys are optional. The system will use fallback values if APIs are not configured.

## AI Features

### Fault Detection
- Uses Convolutional Neural Networks (CNN) for image analysis
- Detects: cracks, dirt, shading, discoloration
- Accuracy: ≥90% (when model is trained)
- **Note**: Currently uses mock data. Train and integrate your CNN model in `solar/utils.py`

### Chatbot
- Rule-based responses (basic implementation)
- Can be upgraded to OpenAI API or Dialogflow
- Provides guidance on solar energy topics
- Accessible via floating widget on all pages

## Database Models

- **UserProfile**: Extended user information
- **ServiceProvider**: Service provider details and verification
- **SolarEstimation**: Stores calculation results
- **Appliance**: Common household appliances (for future use)
- **FaultDetection**: AI detection results
- **ServiceRequest**: User-service provider interactions

## Admin Panel

Access the admin panel at `/admin/` to:
- Manage users and service providers
- Verify service provider accounts
- View all estimations and fault detections
- Monitor service requests

## Development Notes

### Adding API Keys
1. Get API keys from respective providers
2. Add them to environment variables or `.env` file
3. Update `sunsavvy/settings.py` to read from environment

### Training AI Model
1. Collect solar panel images dataset
2. Label images (crack, dirt, normal, etc.)
3. Train CNN model using TensorFlow/Keras
4. Save model and update `detect_fault_ai()` in `solar/utils.py`

### Customizing Calculations
- Edit `solar/utils.py` for calculation logic
- Adjust panel costs, efficiency, and rates in `calculate_financial_analysis()`
- Modify solar irradiance fallback values

## Production Deployment

1. Set `DEBUG = False` in `settings.py`
2. Update `SECRET_KEY` with a secure random key
3. Configure proper database (MySQL/PostgreSQL)
4. Set up static file serving (WhiteNoise or CDN)
5. Configure HTTPS
6. Set up proper error logging
7. Use environment variables for sensitive data

## Testing

Run Django tests:
```bash
python manage.py test
```

## Contributing

This is a Final Year Project. For questions or issues, contact the development team.

## License

This project is developed for academic purposes as part of FYP.

## Authors

- Muhammad Shoaib (CIIT/SP22-BCS-195/ATD)
- Naveed ul Hassan (CIIT/SP22-BCS-197/ATD)
- Rizwan Haider (CIIT/SP22-BCS-198/ATD)

**Supervisor**: Ma'am Hifza Ali

## Acknowledgments

- COMSATS University Islamabad, Abbottabad Campus
- Bootstrap for UI framework
- Django community for excellent documentation

---

**Note**: This application is for estimation purposes. Results may vary. Always consult with professional solar installers for accurate assessments.

