@echo off
echo ========================================
echo URL Attack Detector - Complete Setup
echo ========================================
echo.

echo [1/5] Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)
echo.

echo [2/5] Installing Python dependencies...
cd backend
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install Python dependencies
    pause
    exit /b 1
)
echo.

echo [3/5] Generating training dataset...
python scripts/generate_dataset.py
if %errorlevel% neq 0 (
    echo ERROR: Failed to generate dataset
    pause
    exit /b 1
)
echo.

echo [4/5] Training ML model (this may take 2-5 minutes)...
python scripts/train_model.py
if %errorlevel% neq 0 (
    echo ERROR: Failed to train model
    pause
    exit /b 1
)
echo.

echo [5/5] Generating sample test files...
python scripts/generate_sample_logs.py
if %errorlevel% neq 0 (
    echo WARNING: Failed to generate sample files (optional)
)
echo.

cd ..

echo ========================================
echo Setup completed successfully!
echo ========================================
echo.
echo Next steps:
echo 1. Start the backend server:
echo    cd backend ^&^& python app.py
echo.
echo 2. In a new terminal, start the frontend:
echo    npm install ^&^& npm run dev
echo.
echo 3. Open http://localhost:5173 in your browser
echo.
pause
