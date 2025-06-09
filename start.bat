@echo off
echo ================================
echo  Code2MARKDOWN Launcher
echo ================================
echo.

REM Check if we're in the correct directory
if not exist "app.py" (
    echo ❌ Error: app.py not found. Please run this script from the project root.
    pause
    exit /b 1
)

REM Activate virtual environment if it exists
if exist ".venv\Scripts\activate.bat" (
    echo 🔄 Activating virtual environment...
    call .venv\Scripts\activate.bat
) else (
    echo ⚠️  Virtual environment not found. Using system Python.
)

REM Check if required packages are installed
echo 🔍 Checking dependencies...
python -c "from pybars import Compiler; import streamlit; print('✅ All dependencies are available')" 2>nul
if errorlevel 1 (
    echo ❌ Missing dependencies. Installing...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Failed to install dependencies.
        pause
        exit /b 1
    )
)

echo.
echo 🚀 Starting Code2MARKDOWN application...
echo 📱 The app will open in your default browser
echo 🛑 Press Ctrl+C in this window to stop the server
echo.

streamlit run app.py

echo.
echo 👋 Application stopped.
pause