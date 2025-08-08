#!/usr/bin/env python3
"""
Простой тест исправлений без Streamlit
"""

import html
import os
import xml.etree.ElementTree as ET
from datetime import datetime
from xml.dom import minidom


def is_binary_file(file_path):
    """Определяет, является ли файл бинарным по расширению и содержимому"""
    binary_extensions = {
        ".pyc",
        ".pyo",
        ".so",
        ".dll",
        ".exe",
        ".bin",
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".bmp",
        ".tiff",
        ".ico",
        ".zip",
        ".tar",
        ".gz",
        ".rar",
        ".7z",
        ".pdf",
        ".doc",
        ".docx",
        ".xls",
        ".xlsx",
        ".ppt",
        ".pptx",
        ".mp3",
        ".mp4",
        ".avi",
        ".mov",
        ".mkv",
        ".sqlite",
        ".db",
        ".sqlite3",
    }

    # Проверяем расширение файла
    _, ext = os.path.splitext(file_path.lower())
    if ext in binary_extensions:
        return True

    # Если файл существует, проверяем содержимое
    if os.path.exists(file_path):
        try:
            with open(file_path, "rb") as f:
                chunk = f.read(1024)
                if b"\x00" in chunk:  # Null byte indicates binary file
                    return True
        except OSError:
            return True

    return False


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


def test_binary_detection():
    """Тестируем определение бинарных файлов"""
    print("=== Тест определения бинарных файлов ===")

    # Тестируем расширения
    test_files = [
        "test.py",  # текстовый
        "test.pyc",  # бинарный
        "image.jpg",  # бинарный
        "doc.txt",  # текстовый
        "lib.so",  # бинарный
    ]

    for file_path in test_files:
        is_binary = is_binary_file(file_path)
        print(f"{file_path}: {'BINARY' if is_binary else 'TEXT'}")

    print()


def test_xml_cleaning():
    """Тестируем очистку XML контента"""
    print("=== Тест очистки XML контента ===")

    # Тестовый контент с проблемными символами
    test_content = (
        "Normal text\x00\x01\x02 with invalid chars\x1f and special symbols: <>&'\""
    )

    cleaned = clean_xml_content(test_content)
    print(f"Исходный: {repr(test_content)}")
    print(f"Очищенный: {repr(cleaned)}")

    print()


def test_xml_conversion():
    """Тестируем конвертацию в XML"""
    print("=== Тест конвертации в XML ===")

    test_markdown = """# Test Project
    
This is a test markdown with special characters: <script>alert('xss')</script>
And some invalid XML chars: \x00\x01\x02

## Code Example
```python
def hello():
    print("Hello, World!")
```
"""

    try:
        xml_result = convert_to_xml(test_markdown, "TestProject")
        print("XML конвертация успешна!")
        print("Первые 500 символов:")
        print(xml_result[:500])
    except Exception as e:
        print(f"Ошибка XML конвертации: {e}")

    print()


if __name__ == "__main__":
    test_binary_detection()
    test_xml_cleaning()
    test_xml_conversion()
    print("Все тесты завершены!")
