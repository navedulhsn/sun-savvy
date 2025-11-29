from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.conf import settings
from ..forms import UserRegistrationForm, ServiceProviderRegistrationForm, AuthorizedPersonRegistrationForm, LoginForm
from ..models import UserProfile, ServiceProvider, AuthorizedPerson

def is_authorized_person(user):
    """Check if user is an authorized person"""
    return hasattr(user, 'authorizedperson') and user.authorizedperson.is_active

def register_selection(request):
    """Role selection page for registration"""
    return render(request, 'solar/register.html')

def register_user(request):
    """User registration"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Create user profile
            UserProfile.objects.create(
                user=user,
                phone=form.cleaned_data.get('phone', ''),
                address=form.cleaned_data.get('address', '')
            )
            
            # Generate verification token
            token = get_random_string(length=32)
            user.userprofile.verification_token = token
            user.userprofile.save()
            
            # Send verification email (mock)
            # send_mail(...)
            
            messages.success(request, 'Registration successful! Please login.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'solar/register_user.html', {'form': form})

def register_service_provider(request):
    """Service provider registration"""
    if request.method == 'POST':
        form = ServiceProviderRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Create service provider profile
            ServiceProvider.objects.create(
                user=user,
                company_name=form.cleaned_data.get('company_name'),
                phone=form.cleaned_data.get('phone'),
                email=user.email,
                address=form.cleaned_data.get('address'),
                city=form.cleaned_data.get('city'),
                state=form.cleaned_data.get('state'),
                zip_code=form.cleaned_data.get('zip_code'),
                services_offered=form.cleaned_data.get('services_offered')
            )
            
            messages.success(request, 'Registration successful! Your account is pending approval.')
            return redirect('login')
    else:
        form = ServiceProviderRegistrationForm()
    
    return render(request, 'solar/register_service_provider.html', {'form': form})

def register_authorized_person(request):
    """Authorized person registration"""
    if request.method == 'POST':
        form = AuthorizedPersonRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Create authorized person profile
            AuthorizedPerson.objects.create(
                user=user,
                full_name=form.cleaned_data.get('full_name'),
                phone=form.cleaned_data.get('phone'),
                email=user.email,
                designation=form.cleaned_data.get('designation')
            )
            
            messages.success(request, 'Registration successful! Please login.')
            return redirect('login')
    else:
        form = AuthorizedPersonRegistrationForm()
    
    return render(request, 'solar/register_authorized_person.html', {'form': form})

def login_view(request):
    """Combined login for all user types with role validation"""
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # Redirect based on role
            if user.is_superuser or user.is_staff:
                return redirect('admin_dashboard')
            elif hasattr(user, 'authorizedperson'):
                return redirect('admin_dashboard')
            elif hasattr(user, 'serviceprovider'):
                return redirect('provider_dashboard')
            else:
                return redirect('dashboard')
    else:
        form = LoginForm()
    
    return render(request, 'solar/login.html', {'form': form})

def logout_view(request):
    """Logout view"""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')

def verify_email(request, token):
    """Email verification"""
    try:
        profile = UserProfile.objects.get(verification_token=token)
        profile.email_verified = True
        profile.verification_token = ''
        profile.save()
        messages.success(request, 'Email verified successfully!')
    except UserProfile.DoesNotExist:
        messages.error(request, 'Invalid verification token.')
    
    return redirect('login')
