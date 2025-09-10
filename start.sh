#!/bin/bash

# Linux startup script for code2markdown Docker container
# Supports both development and production environments

set -euo pipefail

# Configuration
APP_NAME="code2markdown"
DEFAULT_PORT=8501
DEFAULT_HOST="0.0.0.0"
DATA_DIR="/app/data"
LOG_DIR="/app/logs"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to wait for service to be ready
wait_for_service() {
    local host=$1
    local port=$2
    local max_attempts=30
    local attempt=1

    log "Waiting for service to be ready at http://${host}:${port}..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "http://${host}:${port}/_stcore/health" >/dev/null 2>&1; then
            success "Service is ready!"
            return 0
        fi
        
        log "Attempt $attempt/$max_attempts - Service not ready yet, waiting..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    error "Service failed to start after $max_attempts attempts"
    return 1
}

# Function to setup directories
setup_directories() {
    log "Setting up directories..."
    
    # Create data directory if it doesn't exist
    mkdir -p "$DATA_DIR"
    
    # Create logs directory if it doesn't exist
    mkdir -p "$LOG_DIR"
    
    # Set proper permissions
    chmod 755 "$DATA_DIR" "$LOG_DIR"
    
    success "Directories setup complete"
}

# Function to validate environment
validate_environment() {
    log "Validating environment..."
    
    # Check if Python is available
    if ! command_exists python; then
        error "Python is not available in the system"
        exit 1
    fi
    
    # Check if required files exist
    if [ ! -f "pyproject.toml" ]; then
        error "pyproject.toml not found"
        exit 1
    fi
    
    if [ ! -f "src/code2markdown/app.py" ]; then
        error "Main application file not found: src/code2markdown/app.py"
        exit 1
    fi
    
    success "Environment validation complete"
}

# Function to setup Streamlit configuration
setup_streamlit_config() {
    log "Setting up Streamlit configuration..."
    
    # Set environment variables with defaults
    export STREAMLIT_SERVER_PORT=${STREAMLIT_SERVER_PORT:-$DEFAULT_PORT}
    export STREAMLIT_SERVER_ADDRESS=${STREAMLIT_SERVER_ADDRESS:-$DEFAULT_HOST}
    export STREAMLIT_SERVER_HEADLESS=${STREAMLIT_SERVER_HEADLESS:-true}
    export STREAMLIT_BROWSER_GATHER_USAGE_STATS=${STREAMLIT_BROWSER_GATHER_USAGE_STATS:-false}
    
    # Additional Streamlit configuration
    export STREAMLIT_SERVER_ENABLECORS=${STREAMLIT_SERVER_ENABLECORS:-false}
    export STREAMLIT_SERVER_ENABLECSRF_PROTECTION=${STREAMLIT_SERVER_ENABLECSRF_PROTECTION:-true}
    export STREAMLIT_SERVER_MAXUPLOADSIZE=${STREAMLIT_SERVER_MAXUPLOADSIZE:-200}
    
    success "Streamlit configuration complete"
}

# Function to handle signals
handle_signal() {
    local signal=$1
    log "Received signal: $signal"
    log "Shutting down gracefully..."
    
    # Kill any child processes
    pkill -P $$ 2>/dev/null || true
    
    exit 0
}

# Function to cleanup on exit
cleanup() {
    log "Cleaning up..."
    # Add any cleanup tasks here
}

# Function to display usage
usage() {
    cat << EOF
Usage: $0 [OPTIONS]

OPTIONS:
    -p, --port PORT          Port to run the application on (default: $DEFAULT_PORT)
    -h, --host HOST          Host to bind to (default: $DEFAULT_HOST)
    -e, --env ENVIRONMENT    Environment (development|production) (default: production)
    -d, --data-dir DIR       Data directory (default: $DATA_DIR)
    -l, --log-dir DIR        Log directory (default: $LOG_DIR)
    -w, --wait               Wait for service to be ready before exiting
    -v, --verbose            Enable verbose output
    --help                   Show this help message

ENVIRONMENT VARIABLES:
    STREAMLIT_SERVER_PORT    Port to run Streamlit on
    STREAMLIT_SERVER_ADDRESS Host to bind to
    ENVIRONMENT              Environment (development|production)

EXAMPLES:
    $0                                    # Run with defaults
    $0 -p 8080 -h 127.0.0.1              # Custom port and host
    $0 -e development -w                 # Development mode with wait
    $0 --verbose                          # Verbose output
EOF
}

# Parse command line arguments
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -p|--port)
                STREAMLIT_SERVER_PORT="$2"
                shift 2
                ;;
            -h|--host)
                STREAMLIT_SERVER_ADDRESS="$2"
                shift 2
                ;;
            -e|--env)
                ENVIRONMENT="$2"
                shift 2
                ;;
            -d|--data-dir)
                DATA_DIR="$2"
                shift 2
                ;;
            -l|--log-dir)
                LOG_DIR="$2"
                shift 2
                ;;
            -w|--wait)
                WAIT_FOR_SERVICE=true
                shift
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            --help)
                usage
                exit 0
                ;;
            *)
                error "Unknown option: $1"
                usage
                exit 1
                ;;
        esac
    done
}

# Main function
main() {
    log "Starting $APP_NAME..."
    
    # Parse command line arguments
    parse_arguments "$@"
    
    # Set environment
    ENVIRONMENT=${ENVIRONMENT:-production}
    
    # Setup signal handlers
    trap 'handle_signal INT' INT
    trap 'handle_signal TERM' TERM
    trap cleanup EXIT
    
    # Validate environment
    validate_environment
    
    # Setup directories
    setup_directories
    
    # Setup Streamlit configuration
    setup_streamlit_config
    
    # Display configuration
    log "Configuration:"
    log "  Environment: $ENVIRONMENT"
    log "  Port: ${STREAMLIT_SERVER_PORT:-$DEFAULT_PORT}"
    log "  Host: ${STREAMLIT_SERVER_ADDRESS:-$DEFAULT_HOST}"
    log "  Data Directory: $DATA_DIR"
    log "  Log Directory: $LOG_DIR"
    
    # Start the application
    log "Starting Streamlit application..."
    
    # Change to app directory
    cd /app
    
    # Run Streamlit
    if [ "$VERBOSE" = true ]; then
        python -m streamlit run src/code2markdown/app.py \
            --server.port="${STREAMLIT_SERVER_PORT:-$DEFAULT_PORT}" \
            --server.address="${STREAMLIT_SERVER_ADDRESS:-$DEFAULT_HOST}" \
            --server.headless=true \
            --logger.level=debug
    else
        python -m streamlit run src/code2markdown/app.py \
            --server.port="${STREAMLIT_SERVER_PORT:-$DEFAULT_PORT}" \
            --server.address="${STREAMLIT_SERVER_ADDRESS:-$DEFAULT_HOST}" \
            --server.headless=true
    fi &
    
    # Get the PID of the background process
    STREAMLIT_PID=$!
    
    # Wait for service if requested
    if [ "${WAIT_FOR_SERVICE:-false}" = true ]; then
        wait_for_service "${STREAMLIT_SERVER_ADDRESS:-$DEFAULT_HOST}" "${STREAMLIT_SERVER_PORT:-$DEFAULT_PORT}"
    fi
    
    # Wait for the Streamlit process
    wait $STREAMLIT_PID
}

# Run main function
main "$@"