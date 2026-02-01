@echo off
echo Starting EduBot - Fast Educational AI...
echo.

cd backend
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Starting backend server...
python main.py

pause