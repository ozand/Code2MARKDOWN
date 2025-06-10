import os
import sqlite3
from datetime import datetime
import streamlit as st
import pyperclip
import pathspec
from pybars import Compiler
import pandas as pd
import math
import html  # Добавьте этот импорт в начало файла
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom

# Настройка ширины экрана
st.set_page_config(layout="wide")

# Initialize database
def init_db():
    conn = sqlite3.connect('code2markdown.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_path TEXT NOT NULL,
            template_name TEXT NOT NULL,
            markdown_content TEXT NOT NULL,
            reference_url TEXT,
            processed_at DATETIME NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Save to database
def save_to_db(project_path, template_name, markdown_content, reference_url=None):
    conn = sqlite3.connect('code2markdown.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO requests (project_path, template_name, markdown_content, reference_url, processed_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (project_path, template_name, markdown_content, reference_url, datetime.now()))
    conn.commit()
    conn.close()

# Get history
def get_history():
    conn = sqlite3.connect('code2markdown.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM requests ORDER BY processed_at DESC')
    rows = cursor.fetchall()
    conn.close()
    return rows

# Delete record from database
def delete_record(record_id):
    conn = sqlite3.connect('code2markdown.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM requests WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()

# Parse .gitignore file
def parse_gitignore(gitignore_path):
    """Parse .gitignore file and return a PathSpec object."""
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r', encoding='utf-8') as gitignore_file:
            lines = gitignore_file.readlines()
        return pathspec.PathSpec.from_lines('gitwildmatch', lines)
    return pathspec.PathSpec([])

# Check if a path should be excluded
def should_exclude(path, spec):
    """Check if a path should be excluded based on the PathSpec."""
    return spec.match_file(path)

# Get filtered files
def get_filtered_files(path, extensions=None, exclude_folders=None, exclude_files=None):
    if extensions is None:
        extensions = ["css", "tsx", "ts", "js", "mjs", "py", "ipynb", "html", "toml",]
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

# Get project structure
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

# Load template
def load_template(template_name):
    """Load a Handlebars template from the templates directory."""
    template_path = os.path.join("templates", template_name)
    if os.path.exists(template_path):
        with open(template_path, 'r', encoding='utf-8') as template_file:
            return Compiler().compile(template_file.read())
    return None

# Generate Markdown
def generate_markdown(project_path, template_name, reference_url=None):
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
    
    markdown_content = template(context)
    markdown_content = html.unescape(markdown_content)
    save_to_db(project_path, template_name, markdown_content, reference_url)
    return markdown_content

# Функции для конвертации контента в различные форматы
def convert_to_xml(markdown_content, project_name):
    """Конвертирует markdown контент в XML формат"""
    root = ET.Element("project")
    
    # Добавляем метаданные
    metadata = ET.SubElement(root, "metadata")
    ET.SubElement(metadata, "name").text = project_name
    ET.SubElement(metadata, "generated_at").text = datetime.now().isoformat()
    ET.SubElement(metadata, "generator").text = "Code2MARKDOWN"
    
    # Добавляем контент
    content = ET.SubElement(root, "content")
    content.text = markdown_content
    
    # Красивое форматирование XML
    rough_string = ET.tostring(root, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def prepare_file_content(content, file_format, project_path):
    """Подготавливает контент для скачивания в указанном формате"""
    project_name = os.path.basename(os.path.abspath(project_path)) if project_path else "project"
    
    if file_format == "txt":
        return content, f"{project_name}_documentation.txt", "text/plain"
    elif file_format == "md":
        return content, f"{project_name}_documentation.md", "text/markdown"
    elif file_format == "xml":
        xml_content = convert_to_xml(content, project_name)
        return xml_content, f"{project_name}_documentation.xml", "application/xml"
    else:
        return content, f"{project_name}_documentation.txt", "text/plain"

# Функция для отображения истории с пагинацией и улучшенным UI
def display_history_with_pagination(history, page_size=10):
    total_records = len(history)
    total_pages = math.ceil(total_records / page_size)
    
    # Пагинация
    page_number = st.number_input("Страница", min_value=1, max_value=total_pages, value=1, step=1)
    start_index = (page_number - 1) * page_size
    end_index = start_index + page_size
    paginated_history = history[start_index:end_index]    # Отображение заголовков
    col1, col2, col3, col4, col5 = st.columns([1, 4, 2, 2, 3])  # Увеличена последняя колонка для кнопок
    with col1:
        st.markdown("**ID**", help="Уникальный идентификатор записи")
    with col2:
        st.markdown("**Project Path**", help="Путь к проекту")
    with col3:
        st.markdown("**Template**", help="Используемый шаблон")
    with col4:
        st.markdown("**Processed At**", help="Время обработки")
    with col5:
        st.markdown("**Actions**", help="Копировать | Скачать | Удалить")    # Отображение данных
    for record in paginated_history:
        with st.container():
            col1, col2, col3, col4, col5 = st.columns([1, 4, 2, 2, 3])  # Увеличена последняя колонка
            with col1:
                st.markdown(f"{record[0]}")  # ID
            with col2:
                # Извлекаем название финальной папки
                folder_name = os.path.basename(record[1])
                # Добавляем значок "?" с всплывающей подсказкой
                path_col, button_col = st.columns([4, 1])
                with path_col:
                    st.markdown(
                        f"{folder_name} <span style='color: gray;' title='{record[1]}'>❔</span>",
                        unsafe_allow_html=True
                    )
                with button_col:
                    if st.button("📋", key=f"copy_path_{record[0]}", help="Копировать путь"):
                        
                        pyperclip.copy(record[1])
                        st.toast("Путь скопирован в буфер обмена!", icon="✅")  # Временное сообщение
            with col3:
                st.markdown(f"{record[2]}")  # Template
            with col4:
                st.markdown(f"{record[5]}")  # Processed At            with col5:
                # Используем st.columns для размещения кнопок в одной строке
                button_col1, button_col2, button_col3 = st.columns([1, 1, 1])
                with button_col1:
                    if st.button("📋", key=f"copy_{record[0]}", help="Копировать markdown"):
                        pyperclip.copy(record[3])
                        st.toast("Markdown скопирован в буфер обмена!", icon="✅")
                        
                with button_col2:
                    # Кнопка скачивания с выпадающим меню форматов
                    download_format = st.selectbox(
                        "Format",
                        options=["txt", "md", "xml"],
                        key=f"format_{record[0]}",
                        label_visibility="collapsed",
                        help="Выберите формат для скачивания"
                    )
                    
                    # Подготавливаем контент для скачивания
                    file_content, filename, mime_type = prepare_file_content(
                        record[3], download_format, record[1]
                    )
                    
                    st.download_button(
                        label="💾",
                        data=file_content,
                        file_name=filename,
                        mime=mime_type,
                        key=f"download_{record[0]}",
                        help=f"Скачать как {download_format.upper()}"
                    )
                    
                with button_col3:
                    if st.button("🗑️", key=f"delete_{record[0]}", help="Удалить запись"):
                        delete_record(record[0])
                        st.toast("Запись удалена!", icon="🗑️")
                        # Trigger rerun by updating session state
                        st.session_state.rerun = True
            
            # Добавляем тонкий разделитель между записями
            st.markdown("<hr style='margin: 0.5rem 0;'>", unsafe_allow_html=True)

    # Add a check to rerun the app
    if st.session_state.rerun:
        st.session_state.rerun = False  # Reset the flag
        st.rerun()  # Trigger a rerun of the app

# Получаем уникальные пути из истории
def get_unique_project_paths(limit=10):
    """Извлекает уникальные пути из истории запросов."""
    conn = sqlite3.connect('code2markdown.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT DISTINCT project_path
        FROM requests
        ORDER BY processed_at DESC
        LIMIT ?
    ''', (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]

#
# Streamlit UI
st.sidebar.title("Навигация")
page = st.sidebar.radio("Выберите страницу", ["Генерация Markdown", "История запросов"])

# Initialize session state for rerun
if "rerun" not in st.session_state:
    st.session_state.rerun = False

if page == "Генерация Markdown":
    st.title("📄 Project Structure and File Content Generator")

    # Session state initialization
    if 'project_path' not in st.session_state:
        st.session_state.project_path = ""
    if 'markdown_content' not in st.session_state:
        st.session_state.markdown_content = ""
    if 'selected_template' not in st.session_state:
        st.session_state.selected_template = "default_template.hbs"

    # Template options
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

    # Input fields
    st.subheader("🔍 Project Details")

    # Получаем уникальные пути из истории
    unique_paths = get_unique_project_paths(limit=10)

    # Поле ввода с выпадающим списком
    if unique_paths:
        selected_path = st.selectbox(
            "Выберите путь из истории или введите новый:",
            options=unique_paths,
            index=0,
            help="Выберите путь из списка или введите новый вручную."
        )
        project_path = st.text_input(
            "Enter the path to your project folder:",
            value=selected_path,
            placeholder="e.g., /path/to/your/project"
        )
    else:
        project_path = st.text_input(
            "Enter the path to your project folder:",
            value=st.session_state.project_path,
            placeholder="e.g., /path/to/your/project"
        )

    selected_template = st.selectbox("Select a template:", templates, index=templates.index(st.session_state.selected_template))
    reference_url = st.text_input("Enter the reference URL (optional):", placeholder="e.g., https://example.com")    # Action buttons
    st.subheader("🚀 Actions")
    
    # Основные действия
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Generate Markdown", help="Generate Markdown content based on the selected template"):
            if project_path and os.path.isdir(project_path):
                st.session_state.markdown_content = generate_markdown(project_path, selected_template, reference_url)
                st.session_state.project_path = project_path
                st.session_state.selected_template = selected_template
                st.toast("Markdown generated successfully!", icon="✅")
            else:
                st.error("Please provide a valid project directory path.")
    with col2:
        if st.button("📋 Copy to Clipboard", help="Copy the generated Markdown to your clipboard"):
            if st.session_state.markdown_content:
                pyperclip.copy(st.session_state.markdown_content)
                st.toast("Markdown content copied to clipboard!", icon="✅")
            else:
                st.error("No Markdown content to copy. Please generate Markdown first.")
    with col3:
        if st.button("🔄 Refresh", help="Clear the generated Markdown content"):
            st.session_state.markdown_content = ""
            st.toast("Markdown content cleared!", icon="✅")
    
    # Кнопки скачивания
    if st.session_state.markdown_content:
        st.subheader("💾 Download Options")
        download_col1, download_col2, download_col3 = st.columns(3)
        
        with download_col1:
            # Скачивание в формате TXT
            txt_content, txt_filename, txt_mime = prepare_file_content(
                st.session_state.markdown_content, "txt", st.session_state.project_path
            )
            st.download_button(
                label="📄 Download as TXT",
                data=txt_content,
                file_name=txt_filename,
                mime=txt_mime,
                help="Download as plain text file"
            )
        
        with download_col2:
            # Скачивание в формате MD
            md_content, md_filename, md_mime = prepare_file_content(
                st.session_state.markdown_content, "md", st.session_state.project_path
            )
            st.download_button(
                label="📝 Download as MD",
                data=md_content,
                file_name=md_filename,
                mime=md_mime,
                help="Download as Markdown file"
            )
        
        with download_col3:
            # Скачивание в формате XML
            xml_content, xml_filename, xml_mime = prepare_file_content(
                st.session_state.markdown_content, "xml", st.session_state.project_path
            )
            st.download_button(
                label="🗂️ Download as XML",
                data=xml_content,
                file_name=xml_filename,
                mime=xml_mime,
                help="Download as XML file"
            )

    # Display generated Markdown
    if st.session_state.markdown_content:
        st.subheader("📝 Generated Markdown")
        st.text_area("Generated Markdown", st.session_state.markdown_content, height=300, label_visibility="collapsed")

    # Error handling for invalid paths
    if project_path and not os.path.isdir(project_path):
        st.error("The specified path is not a valid directory. Please check the path and try again.")

elif page == "История запросов":
    st.title("📜 История запросов")
    history = get_history()

    if history:
        display_history_with_pagination(history)
    else:
        st.info("История запросов пуста.")