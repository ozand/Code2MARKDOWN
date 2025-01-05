import os
import streamlit as st
import pyperclip
import pathspec
from pybars import Compiler

def parse_gitignore(gitignore_path):
    """Parse .gitignore file and return a PathSpec object."""
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r', encoding='utf-8') as gitignore_file:
            lines = gitignore_file.readlines()
        return pathspec.PathSpec.from_lines('gitwildmatch', lines)
    return pathspec.PathSpec([])

def should_exclude(path, spec):
    """Check if a path should be excluded based on the PathSpec."""
    return spec.match_file(path)

def get_filtered_files(path, extensions=None, exclude_folders=None, exclude_files=None):
    if extensions is None:
        extensions = ["css", "tsx", "ts", "js", "mjs", "py", "ipynb", "html"]
    if exclude_folders is None:
        exclude_folders = ["venv", "env", "json_data", ".venv", ".venv312", ".venv_312", "__pycache__", ".next", "node_modules", "temp", "book", "mybooks", "cache", "mlruns", "data", ".data"]
    if exclude_files is None:
        exclude_files = ["package-lock.json", "package.json", "manifest.json", "App.test.js", "reportWebVitals.js", "setupTests.js", ".gitignore"]
    
    exclude_folders.extend([d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d)) and d.startswith('.')])
    gitignore_path = os.path.join(path, '.gitignore')
    spec = parse_gitignore(gitignore_path)
    
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in exclude_folders and not should_exclude(os.path.join(root, d), spec)]
        for file in files:
            file_path = os.path.join(root, file)
            if file.split('.')[-1] in extensions and file not in exclude_files and not should_exclude(file_path, spec):
                yield file_path

def get_project_structure(path, exclude_folders=None, exclude_files=None, indent_level=0):
    if exclude_folders is None:
        exclude_folders = ["venv", "env", "json_data", ".venv", "__pycache__", ".next", "node_modules", "cache", "mlruns"]
    if exclude_files is None:
        exclude_files = [".gitignore"]
    
    exclude_folders.extend([d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d)) and d.startswith('.')])
    gitignore_path = os.path.join(path, '.gitignore')
    spec = parse_gitignore(gitignore_path)
    
    indent = "    " * indent_level
    structure = ""
    items = sorted(os.listdir(path))
    for item in items:
        item_path = os.path.join(path, item)
        if os.path.isdir(item_path):
            if item not in exclude_folders and not should_exclude(item_path, spec):
                structure += f"{indent}├── {item}/\n"
                structure += get_project_structure(item_path, exclude_folders, exclude_files, indent_level + 1)
        elif os.path.isfile(item_path):
            if item not in exclude_files and not should_exclude(item_path, spec):
                structure += f"{indent}├── {item}\n"
    return structure

def load_template(template_name):
    """Load a Handlebars template from the templates directory."""
    template_path = os.path.join("templates", template_name)
    if os.path.exists(template_path):
        with open(template_path, 'r', encoding='utf-8') as template_file:
            return Compiler().compile(template_file.read())
    return None

def generate_markdown(project_path, template_name):
    template = load_template(template_name)
    if not template:
        st.error(f"Template {template_name} not found.")
        return ""
    
    project_structure = get_project_structure(project_path)
    files = []
    for file_path in get_filtered_files(project_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                file_content = file.read()
            files.append({
                "path": file_path,
                "code": file_content
            })
        except Exception as e:
            st.error(f"Error processing file: {file_path} - {str(e)}")
    
    context = {
        "absolute_code_path": os.path.basename(os.path.abspath(project_path)),
        "source_tree": project_structure,
        "files": files
    }
    
    return template(context)

st.title("Project Structure and File Content Generator")

if 'project_path' not in st.session_state:
    st.session_state.project_path = ""
if 'markdown_content' not in st.session_state:
    st.session_state.markdown_content = ""
if 'selected_template' not in st.session_state:
    st.session_state.selected_template = "default_template.hbs"

templates = [
    "default_template.hbs",
    "binary-exploitation-ctf-solver.hbs",
    "claude-xml.hbs",
    "clean-up-code.hbs",
    "cryptography-ctf-solver.hbs",
    "document-the-code.hbs",
    "find-security-vulnerabilities.hbs",
    "fix-bugs.hbs",
    "improve-performance.hbs",
    "refactor.hbs",
    "reverse-engineering-ctf-solver.hbs",
    "web-ctf-solver.hbs",
    "write-git-commit.hbs",
    "write-github-pull-request.hbs",
    "write-github-readme.hbs"
]

project_path = st.text_input("Enter the path to your project folder:", value=st.session_state.project_path)
selected_template = st.selectbox("Select a template:", templates, index=templates.index(st.session_state.selected_template))

if project_path:
    if os.path.isdir(project_path):
        if st.button("Generate Markdown"):
            st.session_state.markdown_content = generate_markdown(project_path, selected_template)
            st.session_state.project_path = project_path
            st.session_state.selected_template = selected_template
            st.text_area("Generated Markdown", st.session_state.markdown_content, height=300)
        
        if st.button("Copy to Clipboard"):
            if st.session_state.markdown_content:
                pyperclip.copy(st.session_state.markdown_content)
                st.success("Markdown content copied to clipboard!")
            else:
                st.error("No Markdown content to copy. Please generate Markdown first.")
        
        if st.button("Refresh"):
            st.session_state.markdown_content = ""
            st.text_area("Generated Markdown", st.session_state.markdown_content, height=300)
    else:
        st.error("The specified path is not a valid directory.")