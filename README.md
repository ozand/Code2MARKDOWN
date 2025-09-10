# filepath: README.md
# Code2MARKDOWN v1.2.0

![Python](https://img.shields.io/badge/python-v3.12+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-latest-red.svg)
![Version](https://img.shields.io/badge/version-v1.2.0-green.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

Code2MARKDOWN is a powerful Streamlit-based web application that generates structured Markdown documentation from your project's source code. Now with **interactive file selection** and **advanced filtering options** for precise control over documentation generation.

## ✨ Key Features

- 🎯 **Interactive File Selection** - Visual file tree with checkboxes
- ⚙️ **Advanced Filtering** - Custom include/exclude patterns and size limits  
- 📁 **Project Structure Preview** - 3-level deep file tree visualization
- 🚀 **Smart Selection Tools** - Quick selection for all files or code files only
- 📄 **Multiple Templates** - 15+ specialized templates for different use cases
- 💾 **Multi-format Export** - Download as TXT, MD, or XML
- 📊 **History Management** - Track and revisit previous generations
- 🔄 **Real-time Processing** - Instant feedback and live file count

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

# Install dependencies using pyproject.toml
pip install -e .
# For development dependencies:
pip install -e .[dev]

# Alternatively, install dependencies from requirements.txt
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

### Interactive File Selection (New in v1.2.0!)
- **Visual File Tree** - Browse your project structure with up to 3 levels of nesting
- **Checkbox Selection** - Choose exactly which files and folders to include
- **Smart Filtering** - Custom include/exclude patterns and file size limits
- **Quick Selection Tools**:
  - 📂 **Select All** - Include all visible files  
  - 📄 **Code Files Only** - Select programming files automatically
  - 🗑️ **Clear Selection** - Deselect everything
- **Real-time Feedback** - Live file count and instant filtering

### Advanced Configuration
- **Include Patterns** - Specify file extensions (.py, .js, .md) or patterns (*.json)
- **Exclude Patterns** - Skip folders (node_modules, __pycache__) or files (*.log)
- **File Size Limits** - Set maximum file size (1-1000 KB) to exclude large files
- **GitIgnore Support** - Automatically respects .gitignore rules

### Core Features  
- **Multi-template Support**: 15+ specialized templates for different use cases
- **Request History**: SQLite-based storage with pagination
- **Clipboard Integration**: One-click copying of generated content
- **Multi-format Download**: Download results as TXT, MD, or XML files
- **Project Structure Analysis**: Automatic tree generation
- **Enhanced History Management**: Copy, download, or delete previous results

## 🎨 User Interface

The application now features a GitIngest-inspired interface with:

1. **Project Details Section** - Path input and template selection
2. **Filter Settings** - Expandable section for advanced filtering options
3. **File Selection** - Interactive project tree with visual selection
4. **Action Buttons** - Generate, copy, and refresh functionality  
5. **Download Options** - Multiple format export capabilities

See the [Interactive Selection Guide](INTERACTIVE_SELECTION_GUIDE.md) for detailed usage instructions.

## 📋 Available Templates

| Template                            | Purpose                              |
| ----------------------------------- | ------------------------------------ |
| `default_template.hbs`              | Basic project documentation          |
| `document-the-code.hbs`             | Add comprehensive code documentation |
| `write-github-readme.hbs`           | Generate GitHub README files         |
| `find-security-vulnerabilities.hbs` | Security analysis                    |
| `clean-up-code.hbs`                 | Code cleanup suggestions             |

[View all templates](templates/)

## 🔧 Configuration

Customize file processing in [`app.py`](app.py):

```python
extensions = ["css", "tsx", "ts", "js", "py", "html", "toml"]
exclude_folders = ["venv", "node_modules", "__pycache__"]
exclude_files = ["package-lock.json", ".gitignore"]
```

## 💾 Download & Export Options

The application now supports multiple download formats:

### Available Formats

| Format  | Description           | Use Case                    |
| ------- | --------------------- | --------------------------- |
| **TXT** | Plain text format     | Simple documentation, notes |
| **MD**  | Markdown format       | GitHub, documentation sites |
| **XML** | Structured XML format | Data exchange, archival     |

### Download Locations

1. **Main Interface**: After generating Markdown, use the download buttons below the action buttons
2. **History Page**: Each historical record has a format selector and download button
3. **Bulk Operations**: Select format and download individual entries from history

### XML Structure

The XML export includes metadata and structured content:

```xml
<?xml version="1.0" ?>
<project>
  <metadata>
    <name>YourProject</name>
    <generated_at>2024-01-01T12:00:00</generated_at>
    <generator>Code2MARKDOWN</generator>
  </metadata>
  <content>
    [Your generated markdown content]
  </content>
</project>
```

## 🧪 Testing

### Running Tests

To run the test suite:

```bash
# Run all tests
python -m pytest tests/

# Run tests with coverage report
pytest --cov=src --cov-report=xml

# Run tests with HTML coverage report (for local viewing)
pytest --cov=src --cov-report=html
```

The coverage reports will be generated in the project root directory:
- `coverage.xml` - XML format for CI/CD integration
- `htmlcov/` - HTML format for local viewing (open `htmlcov/index.html` in your browser)

See [MAINTENANCE.md](MAINTENANCE.md) for information about dead code removal and dependency auditing.

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

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.