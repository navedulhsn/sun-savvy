@echo off
echo Setting up SunSavvy Project...
echo.

echo Creating virtual environment...
if not exist "env" (
    python -m venv env
)

echo Activating virtual environment...
call env\Scripts\activate

echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Running migrations...
python manage.py makemigrations
python manage.py migrate

echo.
echo Creating superuser...
echo Please enter admin credentials when prompted:
python manage.py createsuperuser

echo.
echo Collecting static files...
python manage.py collectstatic --noinput

echo.
echo Setup complete!
echo.
echo To run the server, use:
echo   python manage.py runserver
echo.
echo Then open http://127.0.0.1:8000 in your browser
pause

