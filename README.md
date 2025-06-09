# filepath: README.md
# Code2MARKDOWN

![Python](https://img.shields.io/badge/python-v3.12+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-latest-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

Code2MARKDOWN is a powerful Streamlit-based web application that generates structured Markdown documentation from your project's source code. Perfect for creating comprehensive project overviews, README files, or technical documentation.

## 🚀 Quick Start

### Option 1: Automated Setup (Windows)
```batch
# Run the setup script to create virtual environment and install dependencies
setup.bat

# Launch the application
start.bat
```

### Option 2: Manual Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/Code2MARKDOWN.git
cd Code2MARKDOWN

# Create virtual environment (recommended)
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

## 📁 Project Structure

```
Code2MARKDOWN/
├── app.py                 # Main Streamlit application
├── main.py               # Entry point module
├── templates/            # Handlebars templates
│   ├── default_template.hbs
│   ├── document-the-code.hbs
│   └── ...
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## 🎯 Features

- **Multi-template Support**: 15+ specialized templates for different use cases
- **Smart File Filtering**: Respects `.gitignore` and common exclusion patterns
- **Request History**: SQLite-based storage with pagination
- **Clipboard Integration**: One-click copying of generated content
- **Project Structure Analysis**: Automatic tree generation

## 📋 Available Templates

| Template | Purpose |
|----------|---------|
| `default_template.hbs` | Basic project documentation |
| `document-the-code.hbs` | Add comprehensive code documentation |
| `write-github-readme.hbs` | Generate GitHub README files |
| `find-security-vulnerabilities.hbs` | Security analysis |
| `clean-up-code.hbs` | Code cleanup suggestions |

[View all templates](templates/)

## 🔧 Configuration

Customize file processing in [`app.py`](app.py):

```python
extensions = ["css", "tsx", "ts", "js", "py", "html", "toml"]
exclude_folders = ["venv", "node_modules", "__pycache__"]
exclude_files = ["package-lock.json", ".gitignore"]
```

## 🔧 Troubleshooting

### Common Issues

#### `ModuleNotFoundError: No module named 'pybars'`
This error occurs when the `pybars3` package is not installed. To fix:

```bash
# Quick fix - install the missing dependency
pip install pybars3

# Or reinstall all dependencies
pip install -r requirements.txt

# Or run the automated setup
setup.bat
```

#### Virtual Environment Issues
If you encounter path-related issues:

1. **Run setup.bat first**: `setup.bat` will create and configure the virtual environment
2. **Make sure you're in the project directory**: The scripts should be run from `Code2MARKDOWN/` folder
3. **Check virtual environment**: Ensure `.venv` folder exists and contains `Scripts/activate.bat`
4. **Manual activation**: Run `.venv\Scripts\activate.bat` then `pip install -r requirements.txt`

#### Port Already in Use
If Streamlit can't start due to port conflicts:

```bash
# Kill existing Streamlit processes (Windows)
taskkill /f /im python.exe /fi "commandline eq *streamlit*"

# Or use a different port
streamlit run app.py --server.port 8502
```

#### Dependencies Installation Failed
If pip install fails:

```bash
# Update pip first
python -m pip install --upgrade pip

# Install core dependencies only
pip install streamlit pybars3 pathspec pyperclip pandas

# Clear pip cache if needed
pip cache purge
```

### Quick Setup Guide

1. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd Code2MARKDOWN
   setup.bat  # This handles everything automatically
   ```

2. **Launch application**:
   ```bash
   start.bat  # Launches with dependency checking
   ```

3. **Manual launch** (if needed):
   ```bash
   .venv\Scripts\activate.bat
   streamlit run app.py
   ```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.