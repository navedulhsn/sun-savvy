# Quick Start Guide - Fix Installation Issues

## Problem
You're using Python 3.13.9, and some packages need newer versions. Also, you need a virtual environment.

## Solution - Follow These Steps:

### Step 1: Create and Activate Virtual Environment

```powershell
# Navigate to project folder (if not already there)
cd C:\Users\Naveed-ul-Hassan\OneDrive\Desktop\FYP-SunSavy

# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1
```

**If you get an execution policy error**, run this first:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

You should see `(venv)` at the start of your prompt after activation.

### Step 2: Upgrade pip

```powershell
python -m pip install --upgrade pip
```

### Step 3: Install Dependencies

```powershell
pip install -r requirements.txt
```

If Pillow still fails, try:
```powershell
pip install Pillow --upgrade --no-cache-dir
```

### Step 4: Run Migrations

```powershell
python manage.py makemigrations
python manage.py migrate
```

### Step 5: Create Admin User

```powershell
python manage.py createsuperuser
```
(Enter username, email, and password when prompted)

### Step 6: Run Server

```powershell
python manage.py runserver
```

Then open: http://127.0.0.1:8000/

---

## Important Notes:

1. **Always activate venv first** - You must see `(venv)` in your prompt
2. **If Pillow fails** - The updated requirements.txt should work, but if not, try installing Pillow separately
3. **TensorFlow removed** - It's optional and can cause issues. Add it later when you train your AI model

## Still Having Issues?

If Pillow installation continues to fail on Python 3.13, consider using Python 3.11 or 3.12:
- Download from python.org
- Use: `py -3.11 -m venv venv` instead

