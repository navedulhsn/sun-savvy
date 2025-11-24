# PowerShell script to install all dependencies
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Installing SunSavvy Dependencies" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment
Write-Host "Step 1: Activating virtual environment..." -ForegroundColor Yellow
if (Test-Path "env\Scripts\Activate.ps1") {
    & ".\env\Scripts\Activate.ps1"
} else {
    Write-Host "Virtual environment not found. Creating one..." -ForegroundColor Yellow
    py -m venv env
    & ".\env\Scripts\Activate.ps1"
}

Write-Host ""
Write-Host "Step 2: Upgrading pip..." -ForegroundColor Yellow
py -m pip install --upgrade pip

Write-Host ""
Write-Host "Step 3: Installing Django..." -ForegroundColor Yellow
py -m pip install django

Write-Host ""
Write-Host "Step 4: Installing all dependencies from requirements.txt..." -ForegroundColor Yellow
py -m pip install -r requirements.txt

Write-Host ""
Write-Host "Step 5: Verifying Django installation..." -ForegroundColor Yellow
py -c "import django; print('Django version:', django.get_version())"

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "You can now run:" -ForegroundColor Cyan
Write-Host "  python manage.py runserver" -ForegroundColor White

