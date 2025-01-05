import os
import streamlit as st
from datetime import datetime
import pyperclip
import pathspec

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
        extensions = ["css", "tsx", "ts", "js",  "mjs", "py", "ipynb", "html"] #"json",
    if exclude_folders is None:
        exclude_folders = ["venv", "env", "json_data", ".venv",  ".venv312",  ".venv_312", "__pycache__", ".next", "node_modules", "temp", "book", "mybooks", "cache", "mlruns", "data", ".data"]
    if exclude_files is None:
        exclude_files = ["package-lock.json", "package.json", "manifest.json", "App.test.js", "reportWebVitals.js", "setupTests.js"]

    # Add all folders starting with a dot to exclude_folders
    exclude_folders.extend([d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d)) and d.startswith('.')])

    # Parse .gitignore file
    gitignore_path = os.path.join(path, '.gitignore')
    spec = parse_gitignore(gitignore_path)

    excluded_folders = set()

    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in exclude_folders and not should_exclude(os.path.join(root, d), spec)]
        for d in dirs:
            if should_exclude(os.path.join(root, d), spec):
                excluded_folders.add(os.path.join(root, d))
        for file in files:
            file_path = os.path.join(root, file)
            if file.split('.')[-1] in extensions and file not in exclude_files and not should_exclude(file_path, spec):
                yield file_path

    return excluded_folders

def get_project_structure(path, exclude_folders=None, indent_level=0):
    if exclude_folders is None:
        exclude_folders = ["venv", "env", "json_data", ".venv", "__pycache__", ".next", "node_modules", "cache", "mlruns"]

    # Add all folders starting with a dot to exclude_folders
    exclude_folders.extend([d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d)) and d.startswith('.')])

    # Parse .gitignore file
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
                structure += get_project_structure(item_path, exclude_folders, indent_level + 1)
            else:
                structure += f"{indent}├── [EXCLUDED] {item}/\n"
        elif os.path.isfile(item_path):
            if not should_exclude(item_path, spec):
                structure += f"{indent}├── {item}\n"

    return structure

def generate_markdown(project_path):
    result = "# Folder Structure\n\nOrganize your project structure for clarity and maintainability.\n\n"

    project_structure = get_project_structure(project_path)
    result += f"```\n{project_structure}```\n\n"

    excluded_folders = get_filtered_files(project_path)

    for file_path in get_filtered_files(project_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                file_content = file.read()

            result += f"### {file_path}\n\n```\n{file_content}\n```\n\n"
        except Exception as e:
            st.error(f"Error processing file: {file_path} - {str(e)}")

    # Add "don't answer, only remember" at the end of the generated Markdown
    result += "don't answer, only remember\n"

    return result, excluded_folders

st.title("Project Structure and File Content Generator")

# Initialize session state variables
if 'project_path' not in st.session_state:
    st.session_state.project_path = ""
if 'markdown_content' not in st.session_state:
    st.session_state.markdown_content = ""
if 'excluded_folders' not in st.session_state:
    st.session_state.excluded_folders = set()

project_path = st.text_input("Enter the path to your project folder:", value=st.session_state.project_path)

if project_path:
    if os.path.isdir(project_path):
        if st.button("Generate Markdown"):
            st.session_state.markdown_content, st.session_state.excluded_folders = generate_markdown(project_path)
            st.session_state.project_path = project_path
            st.text_area("Generated Markdown", st.session_state.markdown_content, height=300)

        if st.button("Copy to Clipboard"):
            if st.session_state.markdown_content:
                pyperclip.copy(st.session_state.markdown_content)
                st.success("Markdown content copied to clipboard!")
            else:
                st.error("No Markdown content to copy. Please generate Markdown first.")

        if st.button("Refresh"):
            st.session_state.markdown_content = ""
            st.session_state.excluded_folders = set()
            st.text_area("Generated Markdown", st.session_state.markdown_content, height=300)

        with st.expander("Excluded Folders"):
            if st.session_state.excluded_folders:
                st.write("The following folders were excluded:")
                for folder in st.session_state.excluded_folders:
                    st.write(f"- {folder}")
            else:
                st.write("No folders were excluded.")
    else:
        st.error("The specified path is not a valid directory.")