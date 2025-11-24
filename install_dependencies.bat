@echo off
echo ========================================
echo Installing SunSavvy Dependencies
echo ========================================
echo.

echo Step 1: Activating virtual environment...
call env\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Virtual environment not found!
    echo Creating virtual environment...
    py -m venv env
    call env\Scripts\activate.bat
)

echo.
echo Step 2: Upgrading pip...
py -m pip install --upgrade pip

echo.
echo Step 3: Installing Django...
py -m pip install django

echo.
echo Step 4: Installing all dependencies from requirements.txt...
py -m pip install -r requirements.txt

echo.
echo Step 5: Verifying Django installation...
py -c "import django; print('Django version:', django.get_version())"

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo You can now run:
echo   python manage.py runserver
echo.
pause

