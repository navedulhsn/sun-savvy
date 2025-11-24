@echo off
echo Activating virtual environment...
call env\Scripts\activate.bat

echo Checking Django installation...
python -c "import django; print('Django version:', django.get_version())" 2>nul
if errorlevel 1 (
    echo Django not found. Installing dependencies...
    pip install -r requirements.txt
)

echo.
echo Running Django check...
python manage.py check

echo.
echo Starting Django server...
python manage.py runserver

