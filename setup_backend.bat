@echo off
echo Setting up Flask Backend...
echo.

cd backend

echo Creating virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate

echo Installing Python dependencies...
pip install -r requirements.txt

echo.
echo Backend setup complete!
echo.
echo Next steps:
echo 1. Copy env.example to .env and update database credentials
echo 2. Make sure MySQL is running and database is created
echo 3. Run: python app.py
echo.

pause


