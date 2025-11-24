# SunSavvy Setup Instructions

## Issue: Pillow Installation Error with Python 3.13

You're using Python 3.13, which is very new. Some packages need updated versions. Follow these steps:

## Step-by-Step Setup

### 1. Create a Virtual Environment (IMPORTANT!)

```powershell
# Create virtual environment
python -m venv venv

# Activate it (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# If you get an execution policy error, run this first:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 2. Upgrade pip

```powershell
python -m pip install --upgrade pip
```

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

**Note**: If Pillow still fails, try installing it separately:
```powershell
pip install Pillow --upgrade
```

### 4. Run Migrations

```powershell
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Superuser

```powershell
python manage.py createsuperuser
```

### 6. Run the Server

```powershell
python manage.py runserver
```

## Alternative: If Pillow Still Fails

If you continue having issues with Pillow on Python 3.13, you have two options:

### Option A: Use Python 3.11 or 3.12 (Recommended)

1. Install Python 3.11 or 3.12 from python.org
2. Create virtual environment with that version:
   ```powershell
   py -3.11 -m venv venv
   # or
   py -3.12 -m venv venv
   ```
3. Then follow steps 2-6 above

### Option B: Install Pillow from Pre-built Wheel

```powershell
pip install --upgrade pip wheel
pip install Pillow --only-binary :all:
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'django'"
- Make sure you activated the virtual environment
- You should see `(venv)` at the start of your command prompt

### "Execution Policy Error"
- Run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
- Then try activating venv again

### "Pillow installation fails"
- Try: `pip install Pillow --upgrade --no-cache-dir`
- Or use Python 3.11/3.12 instead

## Quick Setup Script

You can also use the provided `setup.bat` file, but make sure to activate venv first:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
.\setup.bat
```

