#!/usr/bin/env python3
"""
Тестовый скрипт для проверки исправлений
"""

# Импортируем функции из приложения
import xml.etree.ElementTree as ET

from code2markdown.app import clean_xml_content, convert_to_xml, is_binary_file


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
    except (ET.ParseError, UnicodeDecodeError) as e:
        print(f"Ошибка XML конвертации: {e}")

    print()


if __name__ == "__main__":
    test_binary_detection()
    test_xml_cleaning()
    test_xml_conversion()
    print("Все тесты завершены!")
