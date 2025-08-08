"""
Тесты для функций скачивания в Code2MARKDOWN
"""

import unittest

from code2markdown.app import convert_to_xml, prepare_file_content


class TestDownloadFunctions(unittest.TestCase):
    def setUp(self):
        """Подготовка тестовых данных"""
        self.test_markdown = """# Test Project
This is a test markdown content.

## Features
- Feature 1
- Feature 2

## Usage
```python
print("Hello, World!")
```
"""
        self.test_project_path = "/path/to/test/project"

    def test_convert_to_xml(self):
        """Тест конвертации в XML"""
        result = convert_to_xml(self.test_markdown, "TestProject")

        # Проверяем, что это валидный XML
        self.assertIn('<?xml version="1.0"', result)
        self.assertIn("<project>", result)
        self.assertIn("<metadata>", result)
        self.assertIn("<name>TestProject</name>", result)
        self.assertIn("<generator>Code2MARKDOWN</generator>", result)
        self.assertIn("<content>", result)
        self.assertIn("# Test Project", result)

    def test_prepare_file_content_txt(self):
        """Тест подготовки TXT файла"""
        content, filename, mime_type = prepare_file_content(
            self.test_markdown, "txt", self.test_project_path
        )

        self.assertEqual(content, self.test_markdown)
        self.assertEqual(filename, "project_documentation.txt")
        self.assertEqual(mime_type, "text/plain")

    def test_prepare_file_content_md(self):
        """Тест подготовки MD файла"""
        content, filename, mime_type = prepare_file_content(
            self.test_markdown, "md", self.test_project_path
        )

        self.assertEqual(content, self.test_markdown)
        self.assertEqual(filename, "project_documentation.md")
        self.assertEqual(mime_type, "text/markdown")

    def test_prepare_file_content_xml(self):
        """Тест подготовки XML файла"""
        content, filename, mime_type = prepare_file_content(
            self.test_markdown, "xml", self.test_project_path
        )

        self.assertIn('<?xml version="1.0"', content)
        self.assertEqual(filename, "project_documentation.xml")
        self.assertEqual(mime_type, "application/xml")

    def test_prepare_file_content_invalid_format(self):
        """Тест с неверным форматом (должен вернуть TXT по умолчанию)"""
        content, filename, mime_type = prepare_file_content(
            self.test_markdown, "invalid", self.test_project_path
        )

        self.assertEqual(content, self.test_markdown)
        self.assertEqual(filename, "project_documentation.txt")
        self.assertEqual(mime_type, "text/plain")

    def test_xml_metadata_format(self):
        """Тест корректности метаданных в XML"""
        result = convert_to_xml(self.test_markdown, "TestProject")

        # Проверяем структуру XML
        self.assertIn("<metadata>", result)
        self.assertIn("<name>TestProject</name>", result)
        self.assertIn("<generated_at>", result)
        self.assertIn("<generator>Code2MARKDOWN</generator>", result)
        self.assertIn("</metadata>", result)
        self.assertIn("<content>", result)
        self.assertIn("</content>", result)
        self.assertIn("</project>", result)


if __name__ == "__main__":
    unittest.main()
