# Quick Fix for Django Import Error

## The Problem
You're getting: `ImportError: Couldn't import Django. Are you sure it's installed...`

This means the virtual environment is not activated or Django is not installed.

## Solution

### Option 1: Use the PowerShell Script (Recommended)
Run this in PowerShell:
```powershell
cd d:\FYP-SunSavy
.\activate_and_install.ps1
```

### Option 2: Manual Steps

1. **Activate the virtual environment:**
   ```powershell
   cd d:\FYP-SunSavy
   .\env\Scripts\Activate.ps1
   ```

2. **If you get an execution policy error, run this first:**
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

3. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Verify Django is installed:**
   ```powershell
   python -c "import django; print(django.get_version())"
   ```

5. **Run the server:**
   ```powershell
   python manage.py runserver
   ```

### Option 3: Use the Batch File
```cmd
activate_and_run.bat
```

## If Virtual Environment Doesn't Exist

If the `env` folder doesn't exist or is corrupted:

1. **Create a new virtual environment:**
   ```powershell
   python -m venv env
   ```

2. **Activate it:**
   ```powershell
   .\env\Scripts\Activate.ps1
   ```

3. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Run migrations:**
   ```powershell
   python manage.py migrate
   ```

5. **Start the server:**
   ```powershell
   python manage.py runserver
   ```

## Troubleshooting

- **If PowerShell execution is blocked:** Run `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`
- **If pip is not found:** Make sure Python is installed and in your PATH
- **If Django still not found after activation:** Make sure you activated the correct virtual environment

