from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import ServiceProvider, AuthorizedPerson, SolarEstimation, ServiceRequest, FaultDetection


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class ServiceProviderRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    company_name = forms.CharField(max_length=200, required=True)
    phone = forms.CharField(max_length=20, required=True)
    address = forms.CharField(widget=forms.Textarea, required=True)
    city = forms.CharField(max_length=100, required=True)
    state = forms.CharField(max_length=100, required=True)
    zip_code = forms.CharField(max_length=20, required=True)
    services_offered = forms.CharField(
        max_length=200,
        required=True,
        help_text="e.g., Installation, Repair, Maintenance"
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class SolarEstimationForm(forms.ModelForm):
    location_method = forms.ChoiceField(
        choices=[
            ('coordinates', 'Enter Latitude & Longitude'),
            ('map', 'Select Location on Map'),
        ],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        required=True,
        initial='map'
    )
    latitude = forms.DecimalField(
        max_digits=9,
        decimal_places=6,
        required=False,
        help_text="Enter latitude (e.g., 35.3082)"
    )
    longitude = forms.DecimalField(
        max_digits=9,
        decimal_places=6,
        required=False,
        help_text="Enter longitude (e.g., 75.6167)"
    )
    address = forms.CharField(max_length=500, required=True)
    city = forms.CharField(max_length=100, required=True)
    state = forms.CharField(max_length=100, required=True)
    monthly_consumption_kwh = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=True,
        min_value=0,
        help_text="Your average monthly electricity consumption in kWh"
    )
    rooftop_length = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=True,
        min_value=0,
        help_text="Rooftop length in meters"
    )
    rooftop_width = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=True,
        min_value=0,
        help_text="Rooftop width in meters"
    )
    
    class Meta:
        model = SolarEstimation
        fields = [
            'location_method', 'latitude', 'longitude', 'address', 'city', 'state',
            'monthly_consumption_kwh', 'rooftop_length', 'rooftop_width'
        ]
    
    def clean(self):
        cleaned_data = super().clean()
        location_method = cleaned_data.get('location_method')
        latitude = cleaned_data.get('latitude')
        longitude = cleaned_data.get('longitude')
        
        if location_method == 'coordinates':
            if not latitude or not longitude:
                raise forms.ValidationError('Please enter both latitude and longitude when using coordinates method.')
        
        return cleaned_data


class ServiceRequestForm(forms.ModelForm):
    service_type = forms.ChoiceField(
        choices=[
            ('Installation', 'Installation'),
            ('Repair', 'Repair'),
            ('Maintenance', 'Maintenance'),
        ],
        required=True
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        required=True
    )
    address = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=True
    )
    phone = forms.CharField(max_length=20, required=True)
    
    class Meta:
        model = ServiceRequest
        fields = ['service_type', 'description', 'address', 'phone']


class AuthorizedPersonRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    full_name = forms.CharField(max_length=200, required=True)
    phone = forms.CharField(max_length=20, required=True)
    designation = forms.CharField(max_length=100, required=True, help_text="e.g., Admin, Manager, Supervisor")
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class FaultDetectionForm(forms.ModelForm):
    image = forms.ImageField(
        required=True,
        help_text="Upload an image of your solar panel"
    )
    
    class Meta:
        model = FaultDetection
        fields = ['image']


class ServiceProviderProfileForm(forms.ModelForm):
    """Comprehensive form for service provider profile management"""
    
    class Meta:
        model = ServiceProvider
        fields = [
            'company_name', 'phone', 'email', 'address', 'city', 'state', 'zip_code',
            'company_logo', 'business_description', 'years_in_business', 'business_hours',
            'website', 'service_areas', 'service_radius', 'services_offered',
            'license_number', 'certifications', 'price_per_watt', 'installation_cost_per_watt'
        ]
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'zip_code': forms.TextInput(attrs={'class': 'form-control'}),
            'company_logo': forms.FileInput(attrs={'class': 'form-control'}),
            'business_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'years_in_business': forms.NumberInput(attrs={'class': 'form-control'}),
            'business_hours': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Mon-Fri 9AM-5PM'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'service_areas': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'e.g., New York, Brooklyn, Queens'}),
            'service_radius': forms.NumberInput(attrs={'class': 'form-control'}),
            'services_offered': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Installation, Repair, Maintenance'}),
            'license_number': forms.TextInput(attrs={'class': 'form-control'}),
            'certifications': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'price_per_watt': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'installation_cost_per_watt': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
