# Interactive File Selection Guide

## Overview
Code2MARKDOWN v1.2.0 introduces advanced file selection and filtering capabilities, allowing you to precisely control which files are included in your documentation.

## New Features

### 1. Filter Settings ⚙️
Configure which files to include or exclude from processing:

#### Include File Types
- Specify file extensions (e.g., `.py`, `.js`, `.md`)
- Use patterns (e.g., `*.json`, `config.*`)
- One pattern per line

#### Exclude Patterns  
- Exclude specific folders (e.g., `node_modules`, `__pycache__`)
- Exclude file patterns (e.g., `*.log`, `temp*`)
- One pattern per line

#### File Size Limit
- Set maximum file size in KB (1-1000 KB)
- Files larger than limit are automatically excluded
- Default: 50 KB

### 2. Interactive File Selection 📁
Visual file tree with checkboxes for precise file selection:

#### Project Structure View
- Shows up to 3 levels of nesting
- Real-time filtering based on your settings
- 📁 Folders and 📄 files with size information

#### Selection Tools
- **📂 Select All**: Include all visible files
- **📄 Code Files Only**: Select only programming files (.py, .js, .ts, etc.)
- **🗑️ Clear Selection**: Deselect everything

#### Smart Selection
- Selecting a folder automatically includes all its contents
- File count display shows how many files are selected
- Changes apply immediately

## Workflow

### Basic Usage
1. **Enter Project Path** - Point to your project directory
2. **Configure Filters** - Set include/exclude patterns and size limits
3. **Select Files** - Use the interactive tree to choose specific files
4. **Generate** - Create documentation with only selected content

### Advanced Filtering
1. **Start with Broad Filters** - Set basic include/exclude patterns
2. **Preview Structure** - See which files match your criteria  
3. **Fine-tune Selection** - Use checkboxes to refine your choice
4. **Quick Selection** - Use preset buttons for common scenarios

## Examples

### Web Development Project
```
Include: .js, .ts, .jsx, .tsx, .css, .html, .md
Exclude: node_modules, dist, build, *.min.js
Max Size: 100 KB
```

### Python Project
```
Include: .py, .ipynb, .yml, .yaml, .txt, .md
Exclude: __pycache__, .venv, *.pyc, temp, data
Max Size: 50 KB
```

### Documentation Only
```
Include: .md, .txt, .rst
Exclude: .git, temp, backup
Max Size: 25 KB
```

## Tips

### Efficient Selection
- Use **Code Files Only** for technical documentation
- Use **Select All** then deselect unwanted files
- Start with restrictive filters, then expand as needed

### Performance
- Smaller file size limits improve processing speed
- Excluding large folders (node_modules, .git) speeds up tree loading
- Preview shows file count to estimate processing time

### File Organization
- Selected files appear in the documentation in alphabetical order
- Folder structure is preserved in the output
- Only selected files contribute to the final markdown

## Troubleshooting

### Tree Not Loading
- Check that the project path exists and is accessible
- Ensure you have read permissions for the directory
- Try reducing the maximum file size limit

### No Files Visible
- Check your include patterns - they might be too restrictive
- Remove exclude patterns temporarily
- Verify the project contains files matching your criteria

### Slow Performance
- Reduce file size limit
- Add more exclude patterns for large folders
- Limit selection to specific file types only

---

*This feature makes Code2MARKDOWN much more flexible and user-friendly, giving you complete control over documentation generation!*
