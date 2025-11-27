@echo off
echo Starting Isometric Image Transformer Server...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again.
    pause
    exit /b 1
)

REM Start the Flask server in the background and open browser after a delay
start "Isometric Server" cmd /k "python app.py"

REM Wait a few seconds for the server to start
timeout /t 3 /nobreak >nul

REM Open the browser to the application
start http://localhost:5000

echo.
echo Server is starting...
echo Browser should open automatically to http://localhost:5000
echo.
echo To stop the server, close the "Isometric Server" window.
pause

