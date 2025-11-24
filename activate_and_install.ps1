# PowerShell script to activate virtual environment and install dependencies
Write-Host "Activating virtual environment..." -ForegroundColor Green
& ".\env\Scripts\Activate.ps1"

Write-Host "`nChecking if Django is installed..." -ForegroundColor Yellow
python -c "import django; print('Django version:', django.get_version())" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Django not found. Installing dependencies from requirements.txt..." -ForegroundColor Yellow
    pip install -r requirements.txt
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Dependencies installed successfully!" -ForegroundColor Green
    } else {
        Write-Host "Error installing dependencies. Please check the error messages above." -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "Django is already installed!" -ForegroundColor Green
}

Write-Host "`nRunning Django system check..." -ForegroundColor Yellow
python manage.py check

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nAll checks passed! You can now run: python manage.py runserver" -ForegroundColor Green
} else {
    Write-Host "`nThere are some issues. Please check the errors above." -ForegroundColor Red
}

