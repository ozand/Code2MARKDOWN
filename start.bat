@echo off
REM Windows startup script for code2markdown Docker container
REM Supports both development and production environments

setlocal enabledelayedexpansion

REM Configuration
set "APP_NAME=code2markdown"
set "DEFAULT_PORT=8501"
set "DEFAULT_HOST=0.0.0.0"
set "DATA_DIR=/app/data"
set "LOG_DIR=/app/logs"

REM Parse command line arguments
:parse_args
if "%~1"=="" goto :args_done
if /i "%~1"=="-p" (
    set "STREAMLIT_SERVER_PORT=%~2"
    shift
    shift
    goto :parse_args
)
if /i "%~1"=="-h" (
    set "STREAMLIT_SERVER_ADDRESS=%~2"
    shift
    shift
    goto :parse_args
)
if /i "%~1"=="-e" (
    set "ENVIRONMENT=%~2"
    shift
    shift
    goto :parse_args
)
if /i "%~1"=="-d" (
    set "DATA_DIR=%~2"
    shift
    shift
    goto :parse_args
)
if /i "%~1"=="-l" (
    set "LOG_DIR=%~2"
    shift
    shift
    goto :parse_args
)
if /i "%~1"=="-w" (
    set "WAIT_FOR_SERVICE=true"
    shift
    goto :parse_args
)
if /i "%~1"=="-v" (
    set "VERBOSE=true"
    shift
    goto :parse_args
)
if /i "%~1"=="--help" (
    call :usage
    exit /b 0
)
echo Unknown option: %~1
call :usage
exit /b 1

:args_done

REM Set defaults
if not defined ENVIRONMENT set "ENVIRONMENT=production"
if not defined STREAMLIT_SERVER_PORT set "STREAMLIT_SERVER_PORT=%DEFAULT_PORT%"
if not defined STREAMLIT_SERVER_ADDRESS set "STREAMLIT_SERVER_ADDRESS=%DEFAULT_HOST%"

REM Display startup message
echo [INFO] Starting %APP_NAME%...
echo [INFO] Environment: %ENVIRONMENT%
echo [INFO] Port: %STREAMLIT_SERVER_PORT%
echo [INFO] Host: %STREAMLIT_SERVER_ADDRESS%
echo [INFO] Data Directory: %DATA_DIR%
echo [INFO] Log Directory: %LOG_DIR%

REM Set Streamlit environment variables
set "STREAMLIT_SERVER_PORT=%STREAMLIT_SERVER_PORT%"
set "STREAMLIT_SERVER_ADDRESS=%STREAMLIT_SERVER_ADDRESS%"
set "STREAMLIT_SERVER_HEADLESS=true"
set "STREAMLIT_BROWSER_GATHER_USAGE_STATS=false"
set "STREAMLIT_SERVER_ENABLECORS=false"
set "STREAMLIT_SERVER_ENABLECSRF_PROTECTION=true"
set "STREAMLIT_SERVER_MAXUPLOADSIZE=200"

REM Validate environment
call :validate_environment
if errorlevel 1 (
    echo [ERROR] Environment validation failed
    exit /b 1
)

REM Setup directories
call :setup_directories
if errorlevel 1 (
    echo [ERROR] Directory setup failed
    exit /b 1
)

REM Start the application
echo [INFO] Starting Streamlit application...

REM Change to app directory
cd /app

REM Run Streamlit
if "%VERBOSE%"=="true" (
    python -m streamlit run src/code2markdown/app.py ^
        --server.port=%STREAMLIT_SERVER_PORT% ^
        --server.address=%STREAMLIT_SERVER_ADDRESS% ^
        --server.headless=true ^
        --logger.level=debug
) else (
    python -m streamlit run src/code2markdown/app.py ^
        --server.port=%STREAMLIT_SERVER_PORT% ^
        --server.address=%STREAMLIT_SERVER_ADDRESS% ^
        --server.headless=true
)

if errorlevel 1 (
    echo [ERROR] Failed to start Streamlit application
    exit /b 1
)

exit /b 0

:validate_environment
echo [INFO] Validating environment...

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not available in the system
    exit /b 1
)

REM Check if required files exist
if not exist "pyproject.toml" (
    echo [ERROR] pyproject.toml not found
    exit /b 1
)

if not exist "src/code2markdown/app.py" (
    echo [ERROR] Main application file not found: src/code2markdown/app.py
    exit /b 1
)

echo [INFO] Environment validation complete
exit /b 0

:setup_directories
echo [INFO] Setting up directories...

REM Create data directory if it doesn't exist
if not exist "%DATA_DIR%" (
    mkdir "%DATA_DIR%" 2>nul
    if errorlevel 1 (
        echo [WARNING] Failed to create data directory: %DATA_DIR%
    )
)

REM Create logs directory if it doesn't exist
if not exist "%LOG_DIR%" (
    mkdir "%LOG_DIR%" 2>nul
    if errorlevel 1 (
        echo [WARNING] Failed to create log directory: %LOG_DIR%
    )
)

echo [INFO] Directories setup complete
exit /b 0

:usage
echo Usage: %~nx0 [OPTIONS]
echo.
echo OPTIONS:
echo     -p, --port PORT          Port to run the application on (default: %DEFAULT_PORT%)
echo     -h, --host HOST          Host to bind to (default: %DEFAULT_HOST%)
echo     -e, --env ENVIRONMENT    Environment (development^|production) (default: production)
echo     -d, --data-dir DIR       Data directory (default: %DATA_DIR%)
echo     -l, --log-dir DIR        Log directory (default: %LOG_DIR%)
echo     -w, --wait               Wait for service to be ready before exiting
echo     -v, --verbose            Enable verbose output
echo     --help                   Show this help message
echo.
echo ENVIRONMENT VARIABLES:
echo     STREAMLIT_SERVER_PORT    Port to run Streamlit on
echo     STREAMLIT_SERVER_ADDRESS Host to bind to
echo     ENVIRONMENT              Environment (development^|production)
echo.
echo EXAMPLES:
echo     %~nx0                                    # Run with defaults
echo     %~nx0 -p 8080 -h 127.0.0.1              # Custom port and host
echo     %~nx0 -e development -w                 # Development mode with wait
echo     %~nx0 --verbose                          # Verbose output
exit /b 0