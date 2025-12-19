@echo off
echo ========================================
echo  AI Personal Task Automation Agent
echo  Starting Application...
echo ========================================
echo.

REM Check if dependencies are installed
echo [1/3] Checking dependencies...
python -c "import flask" 2>nul
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
)

REM Generate demo data if database doesn't exist
echo.
echo [2/3] Setting up database...
if not exist tasks.db (
    echo Generating demo data...
    python backend/demo_data.py
) else (
    echo Database already exists. Skipping demo data generation.
)

REM Start the server
echo.
echo [3/3] Starting Flask server...
echo.
echo ========================================
echo  Server will start on http://localhost:5000
echo  Press Ctrl+C to stop
echo ========================================
echo.

python backend/app.py
