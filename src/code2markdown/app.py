import fnmatch  # Добавлен глобальный импорт fnmatch
import html  # Добавьте этот импорт в начало файла
import json
import math
import os
import sqlite3
import xml.etree.ElementTree as ET
from datetime import datetime
from xml.dom import minidom

import pathspec
import pyperclip
import streamlit as st
import tornado.iostream
import tornado.websocket
from pybars import Compiler

from code2markdown.application.services import (
    GenerationService,  # Добавлен импорт GenerationService
)
from code2markdown.domain.files import DirectoryNode, FileNode, ProjectTreeBuilder
from code2markdown.domain.filters import FileSize, FilterSettings
from code2markdown.infrastructure.database import SqliteHistoryRepository

# Настройка ширины экрана
st.set_page_config(layout="wide")


# Initialize database
def init_db():
    # Добавление таймаута для операций с базой данных
    try:
        # Используем контекстный менеджер для автоматического закрытия соединения
        with sqlite3.connect("code2markdown.db", timeout=10.0) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_path TEXT NOT NULL,
                    template_name TEXT NOT NULL,
                    markdown_content TEXT NOT NULL,
                    reference_url TEXT,
                    processed_at DATETIME NOT NULL,
                    file_count INTEGER DEFAULT 0,
                    filter_settings TEXT,
                    project_name TEXT
                )
            """)

            # Add new columns if they don't exist (for backward compatibility)
            try:
                cursor.execute(
                    "ALTER TABLE requests ADD COLUMN file_count INTEGER DEFAULT 0"
                )
            except sqlite3.OperationalError:
                pass  # Column already exists

            try:
                cursor.execute("ALTER TABLE requests ADD COLUMN filter_settings TEXT")
            except sqlite3.OperationalError:
                pass  # Column already exists

            try:
                cursor.execute("ALTER TABLE requests ADD COLUMN project_name TEXT")
            except sqlite3.OperationalError:
                pass  # Column already exists

            conn.commit()
            # Соединение автоматически закроется при выходе из блока with
    except sqlite3.OperationalError as e:
        st.error(f"Ошибка подключения к базой данных: {str(e)}")
        try:
            # Попробовать снова с уменьшенным таймаутом
            with sqlite3.connect("code2markdown.db", timeout=5.0) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS requests (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        project_path TEXT NOT NULL,
                        template_name TEXT NOT NULL,
                        markdown_content TEXT NOT NULL,
                        reference_url TEXT,
                        processed_at DATETIME NOT NULL,
                        file_count INTEGER DEFAULT 0,
                        filter_settings TEXT,
                        project_name TEXT
                    )
                """)

                # Add new columns if they don't exist (for backward compatibility)
                try:
                    cursor.execute(
                        "ALTER TABLE requests ADD COLUMN file_count INTEGER DEFAULT 0"
                    )
                except sqlite3.OperationalError:
                    pass  # Column already exists

                try:
                    cursor.execute("ALTER TABLE requests ADD COLUMN filter_settings TEXT")
                except sqlite3.OperationalError:
                    pass  # Column already exists

                try:
                    cursor.execute("ALTER TABLE requests ADD COLUMN project_name TEXT")
                except sqlite3.OperationalError:
                    pass  # Column already exists

                conn.commit()
                # Соединение автоматически закроется при выходе из блока with
        except Exception:
            # Создать новое подключение в случае повторной ошибки
            st.error("Используется временная база данных в памяти")
            with sqlite3.connect(":memory:") as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS requests (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        project_path TEXT NOT NULL,
                        template_name TEXT NOT NULL,
                        markdown_content TEXT NOT NULL,
                        reference_url TEXT,
                        processed_at DATETIME NOT NULL,
                        file_count INTEGER DEFAULT 0,
                        filter_settings TEXT,
                        project_name TEXT
                    )
                """)

                # Add new columns if they don't exist (for backward compatibility)
                try:
                    cursor.execute(
                        "ALTER TABLE requests ADD COLUMN file_count INTEGER DEFAULT 0"
                    )
                except sqlite3.OperationalError:
                    pass  # Column already exists

                try:
                    cursor.execute("ALTER TABLE requests ADD COLUMN filter_settings TEXT")
                except sqlite3.OperationalError:
                    pass  # Column already exists

                try:
                    cursor.execute("ALTER TABLE requests ADD COLUMN project_name TEXT")
                except sqlite3.OperationalError:
                    pass  # Column already exists

                conn.commit()
                # Соединение автоматически закроется при выходе из блока with


init_db()

# Create history repository instance
history_repository = SqliteHistoryRepository()

# Initialize generation service
generation_service = GenerationService(history_repository)


# Get history
def get_history():
    """Retrieve all generation requests from the repository."""
    requests = history_repository.get_all()
    # Convert to legacy format for backward compatibility with existing UI code
    rows = []
    for request in requests:
        rows.append(
            (
                request.id,
                request.project_path,
                request.template_name,
                request.markdown_content,
                request.reference_url,
                request.processed_at.isoformat(),
                request.file_count,
                json.dumps(
                    {
                        "include_patterns": request.filter_settings.include_patterns,
                        "exclude_patterns": request.filter_settings.exclude_patterns,
                        "max_file_size": request.filter_settings.max_file_size.kb,
                        "selected_files_count": len(
                            request.filter_settings.selected_files
                        )
                        if request.filter_settings.selected_files is not None
                        else 0,
                    }
                )
                if request.filter_settings
                else None,
                request.project_name,
            )
        )
    return rows


# Delete record from database
def delete_record(record_id):
    """Delete a generation request by ID."""
    history_repository.delete(record_id)


# Parse .gitignore file
def parse_gitignore(gitignore_path):
    """Parse .gitignore file and return a PathSpec object."""
    if os.path.exists(gitignore_path):
        with open(gitignore_path, encoding="utf-8") as gitignore_file:
            lines = gitignore_file.readlines()
        return pathspec.PathSpec.from_lines("gitwildmatch", lines)
    return pathspec.PathSpec([])


# Check if a path should be excluded
def should_exclude(path, spec):
    """Check if a path should be excluded based on the PathSpec."""
    return spec.match_file(path)


# Check if file is binary
def is_binary_file(file_path):
    """Check if a file is binary by examining its extension and content."""
    # Известные бинарные расширения
    binary_extensions = {
        ".pyc",
        ".pyo",
        ".exe",
        ".dll",
        ".so",
        ".dylib",
        ".bin",
        ".dat",
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".bmp",
        ".tiff",
        ".ico",
        ".mp3",
        ".mp4",
        ".avi",
        ".mkv",
        ".mov",
        ".wmv",
        ".flv",
        ".pdf",
        ".doc",
        ".docx",
        ".xls",
        ".xlsx",
        ".ppt",
        ".pptx",
        ".zip",
        ".rar",
        ".7z",
        ".tar",
        ".gz",
        ".bz2",
        ".sqlite",
        ".db",
        ".dbf",
    }

    # Проверяем расширение
    _, ext = os.path.splitext(file_path.lower())
    if ext in binary_extensions:
        return True

    # Дополнительная проверка: пытаемся прочитать первые несколько байт
    try:
        with open(file_path, "rb") as f:
            chunk = f.read(1024)
            # Если в первых 1024 байтах много нулевых байтов, это вероятно бинарный файл
            if b"\x00" in chunk:
                return True
            # Проверяем на наличие непечатаемых символов
            try:
                chunk.decode("utf-8")
                return False
            except UnicodeDecodeError:
                return True
    except OSError:
        return True

    return False


# Get filtered files
# app.py


def get_filtered_files(path, extensions=None, exclude_folders=None, exclude_files=None):
    if extensions is None:
        extensions = [
            "css",
            "tsx",
            "ts",
            "js",
            "mjs",
            "py",
            "ipynb",
            "html",
            "toml",
        ]
    if exclude_folders is None:
        exclude_folders = [
            "venv",
            "env",
            "json_data",
            ".venv",
            ".venv312",
            ".venv_312",
            "__pycache__",
            ".next",
            "node_modules",
            "temp",
            "book",
            "mybooks",
            "cache",
            "mlruns",
            "data",
            ".data",
            "backup",
            "examples",
            "reports",
            "scripts",
            "tests",
            "model_cache",
            "models",
        ]
    if exclude_files is None:
        exclude_files = [
            "package-lock.json",
            "package.json",
            "manifest.json",
            "App.test.js",
            "reportWebVitals.js",
            "setupTests.js",
            ".gitignore",
            ".env",
        ]

    exclude_folders.extend(
        [
            d
            for d in os.listdir(path)
            if os.path.isdir(os.path.join(path, d)) and d.startswith(".")
        ]
    )
    gitignore_path = os.path.join(path, ".gitignore")
    spec = parse_gitignore(gitignore_path)

    for root, dirs, files in os.walk(path):
        dirs[:] = [
            d
            for d in dirs
            if d not in exclude_folders
            and not should_exclude(os.path.join(root, d), spec)
        ]
        for file in files:
            file_path = os.path.join(root, file)
            if (
                file.split(".")[-1] in extensions
                and file not in exclude_files
                and not should_exclude(file_path, spec)
            ):
                yield file_path


# Get project structure
# app.py


def get_project_structure(path, exclude_folders=None, exclude_files=None, indent_level=0):
    if exclude_folders is None:
        exclude_folders = [
            "venv",
            "env",
            "json_data",
            ".venv",
            "__pycache__",
            ".next",
            "node_modules",
            "cache",
            "mlruns",
            "backup",
            "examples",
            "reports",
            "scripts",
            "tests",
            "model_cache",
            "models",
        ]
    if exclude_files is None:
        exclude_files = [".gitignore", ".env"]

    exclude_folders.extend(
        [
            d
            for d in os.listdir(path)
            if os.path.isdir(os.path.join(path, d)) and d.startswith(".")
        ]
    )
    gitignore_path = os.path.join(path, ".gitignore")
    spec = parse_gitignore(gitignore_path)

    indent = "    " * indent_level
    structure = ""
    items = sorted(os.listdir(path))
    for item in items:
        item_path = os.path.join(path, item)
        if os.path.isdir(item_path):
            if item not in exclude_folders and not should_exclude(item_path, spec):
                structure += f"{indent}├── {item}/\n"
                structure += get_project_structure(
                    item_path, exclude_folders, exclude_files, indent_level + 1
                )
        elif os.path.isfile(item_path):
            if item not in exclude_files and not should_exclude(item_path, spec):
                structure += f"{indent}├── {item}\n"
    return structure


# Load template
def load_template(template_name):
    """Load a Handlebars template from the templates directory."""
    template_path = os.path.join("templates", template_name)
    if os.path.exists(template_path):
        with open(template_path, encoding="utf-8") as template_file:
            return Compiler().compile(template_file.read())
    return None


# Generate Markdown - now just a wrapper around the service
def generate_markdown(
    project_path,
    template_name,
    reference_url=None,
    selected_files=None,
    filter_settings=None,
):
    """
    Wrapper function that delegates to GenerationService.
    Maintains backward compatibility with existing UI code.
    """
    try:
        # Call the service method
        return generation_service.generate_and_save_documentation(
            project_path=project_path,
            template_name=template_name,
            filters=filter_settings,
            reference_url=reference_url,
        )
    except ValueError as e:
        st.error(f"Validation error: {str(e)}")
        raise
    except Exception as e:
        st.error(f"Error generating documentation: {str(e)}")
        raise


def build_structure_from_selected(project_path, selected_files):
    """Строит структуру проекта только для выбранных файлов"""
    structure = f"Project: {os.path.basename(project_path)}\n"

    # Группируем файлы по папкам
    folders: dict = {}
    for file_path in selected_files:
        if os.path.isfile(file_path):
            rel_path = os.path.relpath(file_path, project_path)
            dir_parts = rel_path.split(os.sep)[:-1]
            filename = os.path.basename(file_path)

            current_dict = folders
            for part in dir_parts:
                if part not in current_dict:
                    current_dict[part] = {}
                current_dict = current_dict[part]

            if "_files" not in current_dict:
                current_dict["_files"] = []
            current_dict["_files"].append(filename)

    def build_tree(folder_dict, indent=0):
        result = ""
        indent_str = "    " * indent

        # Сначала выводим папки
        for name, content in folder_dict.items():
            if name != "_files":
                result += f"{indent_str}├── {name}/\n"
                result += build_tree(content, indent + 1)

        # Затем выводим файлы
        if "_files" in folder_dict:
            for filename in sorted(folder_dict["_files"]):
                result += f"{indent_str}├── {filename}\n"

        return result

    structure += build_tree(folders)
    return structure


# Функции для конвертации контента в различные форматы
def convert_to_xml(markdown_content, project_name):
    """Конвертирует markdown контент в XML формат"""
    try:
        root = ET.Element("project")

        # Добавляем метаданные
        metadata = ET.SubElement(root, "metadata")
        ET.SubElement(metadata, "name").text = project_name
        ET.SubElement(metadata, "generated_at").text = datetime.now().isoformat()
        ET.SubElement(metadata, "generator").text = "Code2MARKDOWN"

        # Очищаем markdown контент от недопустимых XML символов
        cleaned_content = clean_xml_content(markdown_content)

        # Добавляем контент с CDATA для безопасности
        content = ET.SubElement(root, "content")
        # Используем CDATA чтобы избежать проблем с специальными символами
        content.text = cleaned_content

        # Красивое форматирование XML
        rough_string = ET.tostring(root, "utf-8")
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")
    except Exception:
        # Если не удается создать валидный XML, возвращаем простую структуру
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<project>
  <metadata>
    <name>{html.escape(project_name)}</name>
    <generated_at>{datetime.now().isoformat()}</generated_at>
    <generator>Code2MARKDOWN</generator>
  </metadata>
  <content><![CDATA[{markdown_content}]]></content>
</project>"""


def clean_xml_content(content):
    """Очищает контент от недопустимых XML символов"""
    if not content:
        return ""

    # Удаляем недопустимые XML символы
    valid_chars = []
    for char in content:
        # XML 1.0 допустимые символы: #x9 | #xA | #xD | [#x20-#xD7FF] | [#xE000-#xFFFD]
        code = ord(char)
        if (
            code == 0x09
            or code == 0x0A
            or code == 0x0D
            or (0x20 <= code <= 0xD7FF)
            or (0xE000 <= code <= 0xFFFD)
        ):
            valid_chars.append(char)
        else:
            # Заменяем недопустимые символы на пробел
            valid_chars.append(" ")

    return "".join(valid_chars)


def prepare_file_content(content, file_format, project_path):
    """Подготавливает контент для скачивания в указанном формате"""
    project_name = (
        os.path.basename(os.path.abspath(project_path)) if project_path else "project"
    )

    if file_format == "txt":
        return content, f"{project_name}_documentation.txt", "text/plain"
    elif file_format == "md":
        return content, f"{project_name}_documentation.md", "text/markdown"
    elif file_format == "xml":
        xml_content = convert_to_xml(content, project_name)
        return xml_content, f"{project_name}_documentation.xml", "application/xml"
    else:
        return content, f"{project_name}_documentation.txt", "text/plain"


# Новые функции для интерактивного выбора файлов
@st.cache_data(ttl=300, max_entries=10, show_spinner=True)
def get_file_tree_structure(
    path,
    max_depth=3,
    current_depth=0,
    include_patterns=None,
    exclude_patterns=None,
    max_file_size=None,
    show_excluded=False,
):
    """Получает структуру файлов для интерактивного отображения"""
    # Создаем экземпляр ProjectTreeBuilder
    builder = ProjectTreeBuilder()

    # Создаем временные FilterSettings для построения дерева
    filters = FilterSettings(
        include_patterns=include_patterns or [],
        exclude_patterns=exclude_patterns or [],
        max_file_size=FileSize(kb=max_file_size) if max_file_size else FileSize(kb=50),
        show_excluded=show_excluded,
        max_depth=max_depth if max_depth is not None and max_depth > 0 else None,
    )

    # Строим дерево с помощью ProjectTreeBuilder
    root_node = builder.build_tree(path, filters)

    # Конвертируем DirectoryNode в структуру словаря
    # Convert DirectoryNode to a dictionary structure
    def convert_to_dict(node, filters):
        result = {}
        if isinstance(node, DirectoryNode):
            for child in node.children:
                if isinstance(child, DirectoryNode):
                    # Recursively convert child directory
                    child_dict = convert_to_dict(child, filters)
                    result[child.name] = {
                        "type": "folder",
                        "path": child.path,
                        "excluded": child.is_excluded(filters),
                        "children": child_dict,
                    }
                elif isinstance(child, FileNode):
                    result[child.name] = {
                        "type": "file",
                        "path": child.path,
                        "excluded": child.is_excluded(filters),
                        "size": child.size,
                    }
            return result
        elif isinstance(node, FileNode):
            return {
                node.name: {
                    "type": "file",
                    "path": node.path,
                    "excluded": node.is_excluded(filters),
                    "size": node.size,
                }
            }
        else:
            return {}

    # Convert root_node to dictionary
    return convert_to_dict(root_node, filters)


def render_file_tree_ui(structure, prefix="", selected_files=None, key_prefix=""):
    """Отображает интерактивное дерево файлов с чекбоксами"""
    if selected_files is None:
        selected_files = set()

    newly_selected: set[str] = set(selected_files)  # Начинаем с текущего выбора
    updated = False  # Флаг для отслеживания изменений

    for name, info in structure.items():
        current_key = f"{key_prefix}_{name}_{hash(info['path'])}"  # Используем hash для уникальности
        indent = "　" * len(prefix.split("├── ")) if prefix else ""

        # Определяем, исключен ли элемент
        is_excluded = info.get("excluded", False)

        if info["type"] == "folder":
            # Получаем пути всех дочерних элементов (включая вложенные)
            child_paths = get_all_child_paths(info, include_excluded=False)
            # Проверяем, выбраны ли все дочерние элементы (только не исключенные)
            all_children_selected = (
                all(path in selected_files for path in child_paths)
                if child_paths
                else False
            )

            # Определяем иконку и стиль для папки
            if is_excluded:
                folder_icon = "❌📁"
                folder_label = f"~~{name}/~~"
                disabled = True
            else:
                folder_icon = "📁"
                folder_label = f"{name}/"
                disabled = False

            # Folder checkbox
            folder_selected = st.checkbox(
                f"{indent}{folder_icon} {folder_label}",
                value=all_children_selected and not is_excluded,
                key=f"folder_{current_key}",
                disabled=disabled,
                help="Исключено фильтрами" if is_excluded else None,
            )

            # Если состояние папки изменилось
            if folder_selected != all_children_selected and not is_excluded:
                updated = True
                if folder_selected:
                    # Выбираем все дочерние элементы (только не исключенные)
                    for child_path in child_paths:
                        newly_selected.add(child_path)
                else:
                    # Снимаем выбор со всех дочерних элементов
                    for child_path in get_all_child_paths(info, include_excluded=True):
                        newly_selected.discard(child_path)

            # Render children and get their selections
            if info.get("children"):
                child_selected = render_file_tree_ui(
                    info["children"],
                    prefix + "├── ",
                    newly_selected,
                    key_prefix + f"_{name}",
                )
                # Update selection with children's state only if there were changes
                if child_selected != newly_selected:
                    newly_selected = child_selected
                    updated = True

        else:
            # File checkbox
            file_size_kb = info["size"] / 1024 if info["size"] > 0 else 0
            size_str = f" ({file_size_kb:.1f} KB)" if file_size_kb > 0 else ""

            # Определяем иконку и стиль для файла
            if is_excluded:
                file_icon = "❌📄"
                file_label = f"~~{name}{size_str}~~"
                disabled = True
            else:
                file_icon = "📄"
                file_label = f"{name}{size_str}"
                disabled = False

            file_selected = st.checkbox(
                f"{indent}{file_icon} {file_label}",
                value=info["path"] in selected_files and not is_excluded,
                key=f"file_{current_key}",
                disabled=disabled,
                help="Исключено фильтрами" if is_excluded else None,
            )

            if not is_excluded:
                if file_selected and info["path"] not in selected_files:
                    newly_selected.add(info["path"])
                    updated = True
                elif not file_selected and info["path"] in newly_selected:
                    newly_selected.discard(info["path"])
                    updated = True

    # Возвращаем обновленный набор только если были изменения
    return newly_selected if updated else selected_files


def get_all_child_paths(folder_info, include_excluded=True):
    """Получает все пути файлов в папке рекурсивно"""
    paths = []

    def collect_paths(structure):
        for name, info in structure.items():
            # Если exclude_excluded=False, пропускаем исключенные элементы
            if not include_excluded and info.get("excluded", False):
                continue

            if info["type"] == "file":
                paths.append(info["path"])
            elif info["type"] == "folder" and info.get("children"):
                collect_paths(info["children"])

    if folder_info.get("children"):
        collect_paths(folder_info["children"])

    return paths


@st.cache_data(ttl=300, max_entries=10)
def get_filtered_files_interactive(
    path,
    selected_files=None,
    include_patterns=None,
    exclude_patterns=None,
    max_file_size=None,
):
    """Получает отфильтрованный список файлов на основе пользовательского выбора"""
    if selected_files is None:
        # Fallback to original logic if no selection
        return get_filtered_files(path)

    # Создаем временные FilterSettings для фильтрации
    filters = FilterSettings(
        include_patterns=include_patterns or [],
        exclude_patterns=exclude_patterns or [],
        max_file_size=FileSize(kb=max_file_size) if max_file_size else FileSize(kb=50),
    )

    # Создаем экземпляр ProjectTreeBuilder
    builder = ProjectTreeBuilder()

    # Строим дерево проекта
    builder.build_tree(path, filters)

    # Фильтруем выбранные файлы
    filtered_files = []
    for file_path in selected_files:
        if os.path.isfile(file_path):
            # Проверяем, не исключен ли файл по фильтрам
            file_node = FileNode(
                path=file_path,
                name=os.path.basename(file_path),
                size=os.path.getsize(file_path) if os.path.exists(file_path) else 0,
                is_binary=builder._is_binary_file(file_path),
            )

            if not file_node.is_excluded(filters):
                filtered_files.append(file_path)
        elif os.path.isdir(file_path):
            # Если выбрана папка, получаем все файлы из неё
            for root, dirs, files in os.walk(file_path):
                for file in files:
                    full_path = os.path.join(root, file)
                    filtered_files.append(full_path)

    return filtered_files


# Функция для отображения истории с пагинацией и улучшенным UI
def display_history_with_pagination(history, page_size=10):
    total_records = len(history)
    total_pages = math.ceil(total_records / page_size) if total_records > 0 else 1

    if total_records == 0:
        st.info("📝 История пуста. Создайте свой первый запрос!")
        return

    # Пагинация
    page_number = st.number_input(
        "Страница", min_value=1, max_value=total_pages, value=1, step=1
    )
    start_index = (page_number - 1) * page_size
    end_index = start_index + page_size
    paginated_history = history[start_index:end_index]

    # Отображение заголовков с улучшенным дизайном
    st.markdown("### 📊 История Запросов")

    # Создаем DataFrame для лучшего отображения
    display_data = []
    for record in paginated_history:
        # record structure: id, project_path, template_name, markdown_content, reference_url, processed_at, file_count, filter_settings, project_name
        record_id = record[0] if len(record) > 0 else "N/A"
        project_path = record[1] if len(record) > 1 else "N/A"
        template_name = record[2] if len(record) > 2 else "N/A"
        markdown_content = record[3] if len(record) > 3 else ""
        reference_url = record[4] if len(record) > 4 else ""
        processed_at = record[5] if len(record) > 5 else "N/A"
        file_count = record[6] if len(record) > 6 else 0
        filter_settings = record[7] if len(record) > 7 else None
        project_name = (
            record[8]
            if len(record) > 8
            else os.path.basename(project_path)
            if project_path != "N/A"
            else "Unknown"
        )

        # Parsing filter settings
        filter_info = "No filters"
        if filter_settings:
            try:
                settings = json.loads(filter_settings)
                include_patterns = settings.get("include_patterns", [])
                exclude_patterns = settings.get("exclude_patterns", [])
                max_file_size = settings.get("max_file_size", 0)
                selected_count = settings.get("selected_files_count", 0)

                filter_parts = []
                if include_patterns:
                    filter_parts.append(
                        f"Include: {', '.join(include_patterns[:3])}{'...' if len(include_patterns) > 3 else ''}"
                    )
                if exclude_patterns:
                    filter_parts.append(
                        f"Exclude: {', '.join(exclude_patterns[:2])}{'...' if len(exclude_patterns) > 2 else ''}"
                    )
                if max_file_size:
                    filter_parts.append(f"Max: {max_file_size}KB")
                if selected_count:
                    filter_parts.append(f"Selected: {selected_count}")

                filter_info = (
                    " | ".join(filter_parts) if filter_parts else "Default filters"
                )
            except (KeyError, TypeError, AttributeError):
                filter_info = "Legacy format"

        display_data.append(
            {
                "ID": record_id,
                "Project": project_name,
                "Template": template_name.replace(".hbs", ""),
                "Files": file_count or 0,
                "Filters": filter_info,
                "Date": processed_at.split(".")[0]
                if processed_at != "N/A"
                else "N/A",  # Remove microseconds
                "Path": project_path,
                "Content": markdown_content,
                "Reference": reference_url,
            }
        )

    # Отображение данных
    for i, data in enumerate(display_data):
        with st.expander(
            f"🗂️ {data['Project']} - {data['Template']} ({data['Date']})", expanded=False
        ):
            # Основная информация
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"**📁 Project:** {data['Project']}")
                st.markdown(f"**📄 Template:** {data['Template']}")
            with col2:
                st.markdown(f"**📊 Files Processed:** {data['Files']}")
                st.markdown(f"**📅 Date:** {data['Date']}")
            with col3:
                st.markdown(
                    f"**🔗 Reference:** {data['Reference'] if data['Reference'] else 'None'}"
                )
                if data["Path"] != "N/A":
                    if st.button(
                        "📋 Copy Path",
                        key=f"copy_path_{data['ID']}",
                        help="Copy project path",
                    ):
                        pyperclip.copy(data["Path"])
                        st.toast("Project path copied!", icon="✅")

            # Информация о фильтрах
            st.markdown(f"**⚙️ Filters Applied:** {data['Filters']}")

            # Полный путь (без вложенного expander)
            if data["Path"] != "N/A":
                st.markdown("**📂 Full Path:**")
                st.code(data["Path"], language=None)

            # Действия
            st.markdown("**🚀 Actions:**")
            action_col1, action_col2, action_col3, action_col4 = st.columns(4)

            with action_col1:
                if st.button(
                    "📋 Copy Content",
                    key=f"copy_content_{data['ID']}",
                    help="Copy markdown content",
                ):
                    pyperclip.copy(data["Content"])
                    st.toast("Content copied to clipboard!", icon="✅")

            with action_col2:
                download_format = st.selectbox(
                    "Format",
                    options=["txt", "md", "xml"],
                    key=f"format_{data['ID']}",
                    help="Select download format",
                )

            with action_col3:
                if data["Content"]:
                    content, filename, mime_type = prepare_file_content(
                        data["Content"], download_format, data["Path"]
                    )
                    st.download_button(
                        label=f"💾 Download {download_format.upper()}",
                        data=content,
                        file_name=filename,
                        mime=mime_type,
                        key=f"download_{data['ID']}_{download_format}",
                    )

            with action_col4:
                if st.button(
                    "🗑️ Delete",
                    key=f"delete_{data['ID']}",
                    help="Delete this record",
                    type="secondary",
                ):
                    delete_record(data["ID"])
                    st.success("Record deleted!")
                    st.rerun()

    # Информация о пагинации
    if total_pages > 1:
        st.markdown(
            f"📄 Showing page {page_number} of {total_pages} ({total_records} total records)"
        )


# Получаем уникальные пути из истории
def get_unique_project_paths(limit=10):
    """Извлекает уникальные пути из истории запросов."""
    conn = sqlite3.connect("code2markdown.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT DISTINCT project_path
        FROM requests
        ORDER BY processed_at DESC
        LIMIT ?
    """,
        (limit,),
    )
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]


# Новые функции для улучшенного управления фильтрами
def read_gitignore_patterns(project_path):
    """Читает паттерны из .gitignore файла"""
    gitignore_path = os.path.join(project_path, ".gitignore")
    patterns = []

    if os.path.exists(gitignore_path):
        try:
            with open(gitignore_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    # Пропускаем пустые строки и комментарии
                    if line and not line.startswith("#"):
                        patterns.append(line)
        except Exception as e:
            st.warning(f"Could not read .gitignore: {str(e)}")

    return patterns


def get_ai_agents_folders(project_path):
    """Получает пути к папкам AI Agents"""
    folders = []

    # Ищем memory-bank папку (RooCode)
    memory_bank_path = os.path.join(project_path, "memory-bank")
    if os.path.isdir(memory_bank_path):
        folders.append(("memory-bank", memory_bank_path, "RooCode"))

    # Ищем .specstory папку (Specstory)
    specstory_path = os.path.join(project_path, ".specstory")
    if os.path.isdir(specstory_path):
        folders.append((".specstory", specstory_path, "Specstory"))

    return folders


def get_docs_folder(project_path):
    """Получает путь к папке docs"""
    docs_path = os.path.join(project_path, "docs")
    if os.path.isdir(docs_path):
        return docs_path
    return None


def select_folder_files(
    folder_path, include_patterns=None, exclude_patterns=None, max_file_size=None
):
    """Выбирает все файлы в указанной папке с учетом фильтров"""
    selected_files: set[str] = set()

    if not os.path.exists(folder_path):
        return selected_files

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)

            # Проверяем размер файла
            if max_file_size:
                try:
                    file_size = os.path.getsize(file_path)
                    if file_size > max_file_size * 1024:  # max_file_size в KB
                        continue
                except (OSError, ValueError):
                    continue

            # Проверяем include patterns
            if include_patterns:
                filename = os.path.basename(file_path)
                file_ext = os.path.splitext(filename)[1].lower()
                should_include = False

                for pattern in include_patterns:
                    pattern = pattern.strip()
                    if not pattern:
                        continue
                    # Если паттерн начинается с точки - это расширение
                    if pattern.startswith("."):
                        if file_ext == pattern.lower():
                            should_include = True
                            break
                    # Если содержит звездочку - это wildcard паттерн
                    elif "*" in pattern:
                        if fnmatch.fnmatch(filename.lower(), pattern.lower()):
                            should_include = True
                            break
                    # Иначе проверяем вхождение в имя файла
                    else:
                        if pattern.lower() in filename.lower():
                            should_include = True
                            break

                if not should_include:
                    continue

            # Проверяем exclude patterns
            if exclude_patterns:
                filename = os.path.basename(file_path)
                should_exclude_file = False

                for pattern in exclude_patterns:
                    pattern = pattern.strip()
                    if not pattern:
                        continue
                    # Если содержит звездочку - это wildcard паттерн
                    if "*" in pattern:
                        if fnmatch.fnmatch(filename.lower(), pattern.lower()):
                            should_exclude_file = True
                            break
                    # Иначе проверяем вхождение
                    else:
                        if pattern.lower() in filename.lower():
                            should_exclude_file = True
                            break

                if should_exclude_file:
                    continue

            selected_files.add(file_path)

    return selected_files


#
# Streamlit UI
st.sidebar.title("Навигация")
page = st.sidebar.radio("Выберите страницу", ["Генерация Markdown", "История запросов"])

# Initialize session state for rerun
if "rerun" not in st.session_state:
    st.session_state.rerun = False

try:
    if page == "Генерация Markdown":
        st.title("📄 Project Structure and File Content Generator")

    # Session state initialization
    if "project_path" not in st.session_state:
        st.session_state.project_path = ""
    if "markdown_content" not in st.session_state:
        st.session_state.markdown_content = ""
    if "selected_template" not in st.session_state:
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
        "write-github-readme.hbs",
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
            help="Выберите путь из списка или введите новый вручную.",
        )
        project_path = st.text_input(
            "Enter the path to your project folder:",
            value=selected_path,
            placeholder="e.g., /path/to/your/project",
        )
    else:
        project_path = st.text_input(
            "Enter the path to your project folder:",
            value=st.session_state.project_path,
            placeholder="e.g., /path/to/your/project",
        )

    selected_template = st.selectbox(
        "Select a template:",
        templates,
        index=templates.index(st.session_state.selected_template),
    )
    reference_url = st.text_input(
        "Enter the reference URL (optional):", placeholder="e.g., https://example.com"
    )

    # Инициализация session state для новых настроек
    # Robust filter settings initialization with fallback
    if "filter_settings" not in st.session_state:
        try:
            st.session_state.filter_settings = FilterSettings(
                include_patterns=[
                    ".py",
                    ".js",
                    ".ts",
                    ".jsx",
                    ".tsx",
                    ".md",
                    ".txt",
                    ".json",
                    ".yml",
                    ".yaml",
                ],
                exclude_patterns=["node_modules", "__pycache__", ".git", "venv", ".venv"],
                max_file_size=FileSize(kb=50),
                show_excluded=False,
            )
        except Exception as e:
            st.error(
                f"Ошибка инициализации фильтров: {str(e)}. Используются настройки по умолчанию."
            )
            st.session_state.filter_settings = FilterSettings(
                include_patterns=["*"],
                exclude_patterns=[],
                max_file_size=FileSize(kb=100),
                show_excluded=True,
            )

    # Новая секция: Настройки фильтров
    st.subheader("⚙️ Filter Settings")

    with st.expander("🔍 File Filtering Options", expanded=False):
        # Быстрые действия с фильтрами
        st.write("**🚀 Quick Actions:**")
        quick_col1, quick_col2, quick_col3, quick_col4 = st.columns(4)

        with quick_col1:
            if st.button(
                "📄 Read .gitignore", help="Add patterns from .gitignore to exclusions"
            ):
                if project_path and os.path.isdir(project_path):
                    gitignore_patterns = read_gitignore_patterns(project_path)
                    if gitignore_patterns:
                        # Добавляем новые паттерны к существующим
                        # Create a new FilterSettings object with updated exclude patterns
                        current_excludes = (
                            st.session_state.filter_settings.exclude_patterns
                        )
                        new_excludes = list(set(current_excludes + gitignore_patterns))
                        try:
                            st.session_state.filter_settings = FilterSettings(
                                include_patterns=st.session_state.filter_settings.include_patterns,
                                exclude_patterns=new_excludes,
                                max_file_size=st.session_state.filter_settings.max_file_size,
                                show_excluded=st.session_state.filter_settings.show_excluded,
                            )
                        except ValueError as e:
                            st.error(
                                f"Ошибка валидации при добавлении паттернов из .gitignore: {str(e)}"
                            )
                        st.toast(
                            f"Added {len(gitignore_patterns)} patterns from .gitignore!",
                            icon="✅",
                        )
                        st.rerun()
                    else:
                        st.toast("No .gitignore found or no patterns to add", icon="ℹ️")
                else:
                    st.error("Please enter a valid project path first")

        with quick_col2:
            # AI Agents folders
            if st.button(
                "🤖 AI Agents Only",
                help="Select only AI Agents folders (memory-bank, .specstory)",
            ):
                if project_path and os.path.isdir(project_path):
                    ai_folders = get_ai_agents_folders(project_path)
                    if ai_folders:
                        selected_files = set()
                        folder_names = []
                        for folder_name, folder_path, agent_type in ai_folders:
                            folder_files = select_folder_files(
                                folder_path,
                                st.session_state.filter_settings.include_patterns,
                                st.session_state.filter_settings.exclude_patterns,
                                st.session_state.filter_settings.max_file_size.kb,
                            )
                            selected_files.update(folder_files)
                            folder_names.append(f"{folder_name} ({agent_type})")

                        try:
                            st.session_state.filter_settings = FilterSettings(
                                include_patterns=st.session_state.filter_settings.include_patterns,
                                exclude_patterns=st.session_state.filter_settings.exclude_patterns,
                                max_file_size=st.session_state.filter_settings.max_file_size,
                                selected_files=selected_files,
                                show_excluded=st.session_state.filter_settings.show_excluded,
                            )
                        except ValueError as e:
                            st.error(f"Ошибка валидации при выборе AI Agents: {str(e)}")
                        st.toast(
                            f"Selected AI Agents: {', '.join(folder_names)}", icon="🤖"
                        )
                        st.rerun()
                    else:
                        st.toast(
                            "No AI Agents folders found (memory-bank, .specstory)",
                            icon="ℹ️",
                        )
                else:
                    st.error("Please enter a valid project path first")

        with quick_col3:
            if st.button("📚 Docs Only", help="Select only files from the docs folder"):
                if project_path and os.path.isdir(project_path):
                    docs_path = get_docs_folder(project_path)
                    if docs_path:
                        docs_files = select_folder_files(
                            docs_path,
                            st.session_state.filter_settings.include_patterns,
                            st.session_state.filter_settings.exclude_patterns,
                            st.session_state.filter_settings.max_file_size.kb,
                        )
                        try:
                            st.session_state.filter_settings = FilterSettings(
                                include_patterns=st.session_state.filter_settings.include_patterns,
                                exclude_patterns=st.session_state.filter_settings.exclude_patterns,
                                max_file_size=st.session_state.filter_settings.max_file_size,
                                selected_files=docs_files,
                                show_excluded=st.session_state.filter_settings.show_excluded,
                            )
                        except ValueError as e:
                            st.error(f"Ошибка валидации при выборе docs folder: {str(e)}")
                        st.toast(
                            f"Selected {len(docs_files)} files from docs folder",
                            icon="📚",
                        )
                        st.rerun()
                    else:
                        st.toast("No docs folder found in project root", icon="ℹ️")
                else:
                    st.error("Please enter a valid project path first")

        with quick_col4:
            if st.button("🔄 Reset Filters", help="Reset all filters to default"):
                try:
                    st.session_state.filter_settings = FilterSettings(
                        include_patterns=[
                            ".py",
                            ".js",
                            ".ts",
                            ".jsx",
                            ".tsx",
                            ".md",
                            ".txt",
                            ".json",
                            ".yml",
                            ".yaml",
                        ],
                        exclude_patterns=[
                            "node_modules",
                            "__pycache__",
                            ".git",
                            "venv",
                            ".venv",
                        ],
                        max_file_size=FileSize(kb=50),
                        show_excluded=False,
                    )
                except ValueError as e:
                    st.error(f"Ошибка сброса фильтров: {str(e)}")
                st.toast("Filters reset to default", icon="🔄")
                st.rerun()

        st.divider()

        col1, col2 = st.columns(2)

        with col1:
            st.write("**Include File Types:**")
            include_input = st.text_area(
                "File extensions or patterns to include (one per line):",
                value="\n".join(st.session_state.filter_settings.include_patterns),
                help="Examples: .py, .js, *.md, config.json",
            )
            try:
                # Create a new FilterSettings object with updated include patterns
                st.session_state.filter_settings = FilterSettings(
                    include_patterns=[
                        pattern.strip()
                        for pattern in include_input.split("\n")
                        if pattern.strip()
                    ],
                    exclude_patterns=st.session_state.filter_settings.exclude_patterns,
                    max_file_size=st.session_state.filter_settings.max_file_size,
                    show_excluded=st.session_state.filter_settings.show_excluded,
                )
            except ValueError as e:
                st.error(f"Ошибка валидации include patterns: {str(e)}")

        with col2:
            st.write("**Exclude Patterns:**")
            exclude_input = st.text_area(
                "Folders or files to exclude (one per line):",
                value="\n".join(st.session_state.filter_settings.exclude_patterns),
                help="Examples: node_modules, __pycache__, *.log, temp",
            )
            try:
                # Create a new FilterSettings object with updated exclude patterns
                st.session_state.filter_settings = FilterSettings(
                    include_patterns=st.session_state.filter_settings.include_patterns,
                    exclude_patterns=[
                        pattern.strip()
                        for pattern in exclude_input.split("\n")
                        if pattern.strip()
                    ],
                    max_file_size=st.session_state.filter_settings.max_file_size,
                    show_excluded=st.session_state.filter_settings.show_excluded,
                )
            except ValueError as e:
                st.error(f"Ошибка валидации exclude patterns: {str(e)}")

        # Ограничение размера файлов
        new_max_size = st.slider(
            "Maximum file size (KB):",
            min_value=1,
            max_value=1000,
            value=st.session_state.filter_settings.max_file_size.kb,
            help="Files larger than this will be excluded",
        )

        # Update filter_settings with new max_file_size if changed
        if new_max_size != st.session_state.filter_settings.max_file_size.kb:
            try:
                st.session_state.filter_settings = FilterSettings(
                    include_patterns=st.session_state.filter_settings.include_patterns,
                    exclude_patterns=st.session_state.filter_settings.exclude_patterns,
                    max_file_size=FileSize(kb=new_max_size),
                    show_excluded=st.session_state.filter_settings.show_excluded,
                )
            except ValueError as e:
                st.error(f"Ошибка валидации максимального размера файла: {str(e)}")

        # Опция показа исключенных файлов
        new_show_excluded = st.checkbox(
            "🔍 Показать исключенные файлы и папки",
            value=st.session_state.filter_settings.show_excluded,
            help="Отображать файлы и папки, исключенные фильтрами (будут неактивны и перечеркнуты)",
        )

        # Update filter_settings with new show_excluded if changed
        if new_show_excluded != st.session_state.filter_settings.show_excluded:
            try:
                st.session_state.filter_settings = FilterSettings(
                    include_patterns=st.session_state.filter_settings.include_patterns,
                    exclude_patterns=st.session_state.filter_settings.exclude_patterns,
                    max_file_size=st.session_state.filter_settings.max_file_size,
                    show_excluded=new_show_excluded,
                )
            except ValueError as e:
                st.error(f"Ошибка валидации настроек отображения: {str(e)}")

    # Новая секция: Предварительный просмотр и выбор файлов
    st.subheader("📁 File Selection")

    # Настройка максимальной глубины сканирования
    max_depth = st.number_input(
        "Макс. глубина сканирования",
        min_value=0,
        value=0,
        help="0 - без ограничений, 1 - только корень, 2 - до 2 уровней",
    )
    current = st.session_state.filter_settings
    st.session_state.filter_settings = FilterSettings(
        include_patterns=current.include_patterns,
        exclude_patterns=current.exclude_patterns,
        max_file_size=current.max_file_size,
        show_excluded=current.show_excluded,
        selected_files=current.selected_files,
        max_depth=max_depth if max_depth > 0 else None,
    )

    # Информационная панель о доступных специальных папках
    if project_path and os.path.isdir(project_path):
        info_col1, info_col2, info_col3 = st.columns(3)

        with info_col1:
            ai_folders = get_ai_agents_folders(project_path)
            if ai_folders:
                folder_info = []
                for folder_name, folder_path, agent_type in ai_folders:
                    file_count = sum(
                        1 for _, _, files in os.walk(folder_path) for _ in files
                    )
                    folder_info.append(
                        f"**{agent_type}** ({folder_name}): {file_count} files"
                    )
                st.info("🤖 **AI Agents Found:**\n" + "\n".join(folder_info))
            else:
                st.info("🤖 **AI Agents:** Not found")

        with info_col2:
            docs_path = get_docs_folder(project_path)
            if docs_path:
                docs_file_count = sum(
                    1 for _, _, files in os.walk(docs_path) for _ in files
                )
                st.info(f"📚 **Docs Folder:** {docs_file_count} files")
            else:
                st.info("📚 **Docs Folder:** Not found")

        with info_col3:
            gitignore_path = os.path.join(project_path, ".gitignore")
            if os.path.exists(gitignore_path):
                gitignore_patterns = read_gitignore_patterns(project_path)
                st.info(f"📄 **.gitignore:** {len(gitignore_patterns)} patterns")
            else:
                st.info("📄 **.gitignore:** Not found")

    if project_path and os.path.isdir(project_path):
        with st.expander("🌳 Project Structure (Select files to include)", expanded=True):
            # Добавлена проверка на существование ProjectTreeBuilder
            try:
                # Кнопка сканирования папки
                if st.button("Сканировать папку", key="scan_button"):
                    # Показываем индикатор загрузки
                    with st.spinner("Scanning project structure..."):
                        # Создаем временные FilterSettings для построения дерева
                        filters = FilterSettings(
                            include_patterns=st.session_state.filter_settings.include_patterns
                            or [],
                            exclude_patterns=st.session_state.filter_settings.exclude_patterns
                            or [],
                            max_file_size=st.session_state.filter_settings.max_file_size,
                            show_excluded=st.session_state.filter_settings.show_excluded,
                            max_depth=st.session_state.filter_settings.max_depth,
                        )

                        # Получаем структуру файлов
                        builder = ProjectTreeBuilder()
                        file_tree = builder.build_tree(project_path, filters)

                        # Конвертируем DirectoryNode в словарь перед сохранением
                        st.session_state.file_tree = get_file_tree_structure(
                            project_path,
                            max_depth=filters.max_depth,
                            include_patterns=filters.include_patterns,
                            exclude_patterns=filters.exclude_patterns,
                            max_file_size=filters.max_file_size.kb,
                            show_excluded=filters.show_excluded,
                        )

                    # Считаем количество файлов и папок
                    def count_items(structure):
                        folders = 0
                        files = 0
                        for name, info in structure.items():
                            if info["type"] == "folder":
                                folders += 1
                                if info.get("children"):
                                    child_folders, child_files = count_items(
                                        info["children"]
                                    )
                                    folders += child_folders
                                    files += child_files
                            else:
                                files += 1
                        return folders, files

                    # Показываем статистику
                    if st.session_state.file_tree:
                        folder_count, file_count = count_items(st.session_state.file_tree)
                        st.success(
                            f"Scan complete: {folder_count} folders, {file_count} files found"
                        )

                # Показываем дерево только если оно существует
                if st.session_state.get("file_tree"):
                    file_tree = st.session_state.file_tree
                    st.write(
                        "**Select files and folders to include in the documentation:**"
                    )

                    # Кнопки быстрого выбора
                    sel_col1, sel_col2, sel_col3 = st.columns(3)
                    with sel_col1:
                        if st.button(
                            "📂 Select All",
                            help="Select all visible files",
                            key="select_all_btn",
                        ):
                            if st.session_state.get("file_tree"):
                                all_paths = []

                                def collect_all_paths(structure):
                                    for name, info in structure.items():
                                        # Пропускаем исключенные элементы
                                        if not info.get("excluded", False):
                                            if info["type"] == "file":
                                                all_paths.append(info["path"])
                                            elif info["type"] == "folder" and info.get(
                                                "children"
                                            ):
                                                # Добавляем только файлы, не папки
                                                collect_all_paths(info["children"])

                                collect_all_paths(st.session_state.file_tree)
                                # Создаем новую FilterSettings с обновленным selected_files
                                current = st.session_state.filter_settings
                                st.session_state.filter_settings = FilterSettings(
                                    include_patterns=current.include_patterns,
                                    exclude_patterns=current.exclude_patterns,
                                    max_file_size=current.max_file_size,
                                    show_excluded=current.show_excluded,
                                    selected_files=set(all_paths),
                                    max_depth=current.max_depth,
                                )
                            else:
                                st.warning("Please scan the project structure first")

                    with sel_col2:
                        if st.button(
                            "📄 Code Files Only",
                            help="Select only code files",
                            key="code_only_btn",
                        ):
                            code_extensions = [
                                ".py",
                                ".js",
                                ".ts",
                                ".jsx",
                                ".tsx",
                                ".java",
                                ".cpp",
                                ".c",
                                ".h",
                            ]
                            code_paths = []

                            def collect_code_paths(structure):
                                for name, info in structure.items():
                                    # Пропускаем исключенные элементы
                                    if not info.get("excluded", False):
                                        if info["type"] == "file":
                                            _, ext = os.path.splitext(name)
                                            if ext.lower() in code_extensions:
                                                code_paths.append(info["path"])
                                        elif info["type"] == "folder" and info.get(
                                            "children"
                                        ):
                                            collect_code_paths(info["children"])

                            collect_code_paths(file_tree)
                            # Создаем новую FilterSettings с обновленным selected_files
                            current = st.session_state.filter_settings
                            st.session_state.filter_settings = FilterSettings(
                                include_patterns=current.include_patterns,
                                exclude_patterns=current.exclude_patterns,
                                max_file_size=current.max_file_size,
                                show_excluded=current.show_excluded,
                                selected_files=set(code_paths),
                                max_depth=current.max_depth,
                            )

                    with sel_col3:
                        if st.button(
                            "🗑️ Clear Selection",
                            help="Deselect all files",
                            key="clear_selection_btn",
                        ):
                            # Создаем новую FilterSettings с пустым selected_files
                            current = st.session_state.filter_settings
                            st.session_state.filter_settings = FilterSettings(
                                include_patterns=current.include_patterns,
                                exclude_patterns=current.exclude_patterns,
                                max_file_size=current.max_file_size,
                                show_excluded=current.show_excluded,
                                selected_files=set(),
                                max_depth=current.max_depth,
                            )

                    # Отображаем количество выбранных файлов
                    selected_count = len(
                        [
                            path
                            for path in st.session_state.filter_settings.selected_files
                            if os.path.isfile(path)
                        ]
                    )
                    st.info(f"📊 Selected files: {selected_count}")

                    # Отладочная информация
                    # st.write(f"DEBUG: selected_files length: {len(st.session_state.filter_settings.selected_files)}")
                    # st.write(f"DEBUG: file_tree keys: {list(st.session_state.file_tree.keys()) if st.session_state.get('file_tree') else 'No file tree'}")

                    # Рендерим дерево файлов с чекбоксами
                    newly_selected = render_file_tree_ui(
                        file_tree,
                        selected_files=st.session_state.filter_settings.selected_files,
                        key_prefix="tree",
                    )

                    # Обновляем выбранные файлы только если есть изменения
                    if newly_selected != st.session_state.filter_settings.selected_files:
                        st.session_state.filter_settings.selected_files = newly_selected
                else:
                    st.info("Нажмите 'Сканировать папку' для отображения структуры")
            except NameError as e:
                st.error(f"ProjectTreeBuilder is not available: {str(e)}")
            except Exception as e:
                st.error(f"Error loading project structure: {str(e)}")
    else:
        st.info("Enter a valid project path to see the file structure.")

    # Action buttons
    st.subheader("🚀 Actions")

    # Основные действия
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button(
            "Generate Markdown",
            help="Generate Markdown content based on the selected template",
        ):
            if project_path and os.path.isdir(project_path):
                # Используем новые настройки фильтров
                current_filters = st.session_state.filter_settings

                try:
                    st.session_state.markdown_content = generate_markdown(
                        project_path,
                        selected_template,
                        reference_url,
                        selected_files=current_filters.selected_files
                        if current_filters.selected_files
                        else None,
                        filter_settings=current_filters,
                    )
                except ValueError as e:
                    st.error(f"Ошибка валидации настроек фильтрации: {str(e)}")
                st.session_state.project_path = project_path
                st.session_state.selected_template = selected_template
                st.toast("Markdown generated successfully!", icon="✅")
            else:
                st.error("Please provide a valid project directory path.")
    with col2:
        if st.button(
            "📋 Copy to Clipboard", help="Copy the generated Markdown to your clipboard"
        ):
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
                help="Download as plain text file",
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
                help="Download as Markdown file",
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
                help="Download as XML file",
            )

    # Display generated Markdown
    if st.session_state.markdown_content:
        st.subheader("📝 Generated Markdown")
        st.text_area(
            "Generated Markdown",
            st.session_state.markdown_content,
            height=300,
            label_visibility="collapsed",
        )

    # Error handling for invalid paths
    if project_path and not os.path.isdir(project_path):
        st.error(
            "The specified path is not a valid directory. Please check the path and try again."
        )

    elif page == "История запросов":
        st.title("📜 История запросов")
        history = get_history()

        if history:
            display_history_with_pagination(history)
        else:
            st.info("История запросов пуста.")

except tornado.iostream.StreamClosedError:
    st.warning("Соединение прервано. Пожалуйста, перезагрузите страницу.")
except tornado.websocket.WebSocketClosedError:
    st.warning("WebSocket соединение закрыто. Пожалуйста, перезагрузите страницу.")
except TimeoutError:
    st.warning("Операция превысила время ожидания. Пожалуйста, попробуйте снова.")
except Exception as e:
    st.error(f"Неожиданная ошибка: {str(e)}")
finally:
    # Гарантировать закрытие всех ресурсов
    # print("Очистка ресурсов...")  # Убрано для уменьшения вывода в терминал

    # Закрываем соединение WebSocket если оно существует
    if hasattr(st, "_websocket") and st._websocket:
        try:
            st._websocket.close()
            # print("WebSocket соединение закрыто успешно")  # Убрано для уменьшения вывода в терминал
        except Exception:
            # print(f"Ошибка при закрытии WebSocket: {str(e)}")  # Убрано для уменьшения вывода в терминал
            pass

    # Закрываем соединение с базой данных если оно открыто
    if "db_conn" in st.session_state and st.session_state.db_conn:
        try:
            st.session_state.db_conn.close()
            # print("Соединение с базой данных закрыто")  # Убрано для уменьшения вывода в терминал
        except Exception:
            # print(f"Ошибка при закрытии базы данных: {str(e)}")  # Убрано для уменьшения вывода в терминал
            pass
