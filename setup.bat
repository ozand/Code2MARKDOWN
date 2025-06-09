@echo off
echo ================================
echo  Code2MARKDOWN Setup
echo ================================
echo.

REM Create virtual environment if it doesn't exist
if not exist ".venv" (
    echo 🔧 Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment.
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call .venv\Scripts\activate.bat

REM Upgrade pip
echo 📦 Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo 📚 Installing dependencies...
pip install -r requirements.txt

REM Test installation
echo 🧪 Testing installation...
python -c "from pybars import Compiler; import streamlit; print('✅ Setup completed successfully!')"

if errorlevel 1 (
    echo ❌ Installation test failed.
    pause
    exit /b 1
)

echo.
echo ✅ Setup completed! You can now run start.bat to launch the application.
pause
