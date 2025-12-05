from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import ServiceProvider, AuthorizedPerson, SolarEstimation, ServiceRequest, FaultDetection, ProviderPanel


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
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken. Please choose a different one.')
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered. Please use a different email or try logging in.')
        return email
    
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
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken. Please choose a different one.')
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered. Please use a different email or try logging in.')
        return email


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
    # Main request category - what user wants
    request_category = forms.ChoiceField(
        choices=[
            ('purchase', 'I want to purchase panels'),
            ('installation', 'I need installation service'),
            ('repair', 'I need repair service'),
            ('maintenance', 'I need maintenance service'),
        ],
        required=True,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_request_category'})
    )
    # Panel type for installation/maintenance
    preferred_panel_type = forms.ChoiceField(
        choices=[
            ('', 'Select Panel Type (Optional)'),
            ('premium', 'Premium Solar Panel'),
            ('large', 'Large Solar Panel'),
            ('medium', 'Medium Solar Panel'),
            ('standard', 'Standard Solar Panel'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_panel_type'})
    )
    # Panel selection for purchase
    selected_panel = forms.ModelChoiceField(
        queryset=None,  # Will be set in __init__
        required=False,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_selected_panel'}),
        help_text="Select panel to purchase"
    )
    quantity = forms.IntegerField(
        required=False,
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'id': 'id_quantity', 'min': '1'}),
        help_text="Quantity"
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        required=True,
        help_text="Describe your requirement"
    )
    address = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        required=True
    )
    phone = forms.CharField(
        max_length=20, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = ServiceRequest
        fields = ['request_category', 'preferred_panel_type', 'selected_panel', 'quantity', 'description', 'address', 'phone']
    
    def __init__(self, *args, **kwargs):
        # Get provider panels for purchase selection
        provider = kwargs.pop('provider', None)
        super().__init__(*args, **kwargs)
        
        # Set panel queryset if provider provided
        if provider:
            from .models import ProviderPanel
            self.fields['selected_panel'].queryset = ProviderPanel.objects.filter(provider=provider, is_active=True)
        else:
            self.fields['selected_panel'].queryset = ProviderPanel.objects.none()


class AuthorizedPersonRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    full_name = forms.CharField(max_length=200, required=True)
    phone = forms.CharField(max_length=20, required=True)
    designation = forms.CharField(max_length=100, required=True, help_text="e.g., Admin, Manager, Supervisor")
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken. Please choose a different one.')
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered. Please use a different email or try logging in.')
        return email


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


class ProviderPanelForm(forms.ModelForm):
    """Form for adding/editing provider panels with predefined panel type selection"""
    
    class Meta:
        model = ProviderPanel
        fields = [
            'panel_type', 'name', 'model_no', 'power_watts', 'efficiency', 'length', 'width',
            'price_pkr', 'installation_price', 'stock', 'warranty_years', 
            'image', 'description', 'is_active'
        ]
        widgets = {
            'panel_type': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Custom name (optional)'}),
            'model_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., SP-500W-MONO-2024'}),
            'power_watts': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'placeholder': 'Power in watts'}),
            'efficiency': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '1', 'placeholder': 'e.g., 0.20 for 20%'}),
            'length': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'placeholder': 'Length in meters'}),
            'width': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'placeholder': 'Width in meters'}),
            'price_pkr': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'placeholder': 'Price in PKR'}),
            'installation_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'placeholder': 'Installation price in PKR'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': 'Available stock'}),
            'warranty_years': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': 'Warranty period in years'}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Panel description, features, specifications...'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Panel type is required for new panels
        self.fields['panel_type'].required = True
        self.fields['panel_type'].help_text = "Select one of the 4 predefined panel types"
        # Name is optional (will use panel type name if not provided)
        self.fields['name'].required = False
        self.fields['efficiency'].required = False
        self.fields['image'].required = False
        self.fields['description'].required = False
        self.fields['model_no'].required = False
        self.fields['length'].required = False
        self.fields['width'].required = False
        self.fields['installation_price'].required = False
