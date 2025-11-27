# Isometric Image Transformer - Startup Script
Write-Host "Starting Isometric Image Transformer Server..." -ForegroundColor Green
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found: $pythonVersion" -ForegroundColor Cyan
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python and try again." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Start the Flask server in a new window
Write-Host "Starting Flask server..." -ForegroundColor Yellow
Start-Process cmd -ArgumentList "/k", "python app.py" -WindowStyle Normal

# Wait for server to start
Write-Host "Waiting for server to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Open the browser
Write-Host "Opening browser at http://localhost:5000" -ForegroundColor Green
Start-Process "http://localhost:5000"

Write-Host ""
Write-Host "Server is running!" -ForegroundColor Green
Write-Host "Browser should open automatically to http://localhost:5000" -ForegroundColor Cyan
Write-Host ""
Write-Host "To stop the server, close the 'Isometric Server' window." -ForegroundColor Yellow
Write-Host ""
Read-Host "Press Enter to exit this window (server will continue running)"

