#!/usr/bin/env python3
"""
Простой тест для проверки работы фильтров
"""

import os
import tempfile
from code2markdown.domain.files import ProjectTreeBuilder
from code2markdown.domain.filters import FileSize, FilterSettings

def test_filter_processing():
    """Тестируем работу фильтров"""
    print("🔍 Тестирование работы фильтров")
    print("=" * 50)
    
    # Создаем временную директорию с тестовыми файлами
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"📁 Временная директория: {temp_dir}")
        
        # Создаем тестовые файлы
        with open(os.path.join(temp_dir, "main.py"), "w") as f:
            f.write("# Main Python file\nprint('Hello')")
            
        with open(os.path.join(temp_dir, "README.md"), "w") as f:
            f.write("# Project Documentation\nThis is a test.")
            
        with open(os.path.join(temp_dir, "test.pyc"), "wb") as f:
            f.write(b"\x00\x01\x02\x03")
        
        # Настройки фильтров
        filters = FilterSettings(
            include_patterns=[".py", ".md"],
            exclude_patterns=["__pycache__", ".git"],
            max_file_size=FileSize(kb=100),
            show_excluded=False,
        )
        
        print(f"📥 Include patterns: {filters.include_patterns}")
        print(f"📤 Exclude patterns: {filters.exclude_patterns}")
        print(f"📊 Max file size: {filters.max_file_size.kb} KB")
        print()
        
        # Строим дерево проекта
        builder = ProjectTreeBuilder()
        root_node = builder.build_tree(temp_dir, filters)
        
        if root_node is not None:
            print("🌳 Структура проекта:")
            def print_tree(node, depth=0):
                indent = "  " * depth
                if hasattr(node, 'children'):
                    print(f"{indent}📁 {node.name}/")
                    for child in node.children:
                        print_tree(child, depth + 1)
                else:
                    print(f"{indent}📄 {node.name} ({node.size} bytes)")
            
            print_tree(root_node)
        else:
            print("❌ Не удалось построить дерево проекта")

if __name__ == "__main__":
    test_filter_processing()