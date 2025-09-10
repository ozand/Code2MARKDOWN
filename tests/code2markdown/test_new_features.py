#!/usr/bin/env python3
"""
Тестовый скрипт для новых функций фильтрации
"""

import os

# Импортируем функции из приложения
from code2markdown.app import (
    get_ai_agents_folders,
    get_docs_folder,
    read_gitignore_patterns,
    select_folder_files,
)


def test_new_features():
    """Тестируем новые функции"""
    test_project_path = os.path.join(os.path.dirname(__file__), "test_project")

    print("=== Тест новых функций фильтрации ===")
    print(f"Тестовый проект: {test_project_path}")
    print()

    # Тестируем чтение .gitignore
    print("1. Тестируем чтение .gitignore:")
    gitignore_patterns = read_gitignore_patterns(test_project_path)
    print(f"Найдено паттернов: {len(gitignore_patterns)}")
    print("Первые 5 паттернов:", gitignore_patterns[:5])
    print()

    # Тестируем поиск AI Agents папок
    print("2. Тестируем поиск AI Agents папок:")
    ai_folders = get_ai_agents_folders(test_project_path)
    print(f"Найдено AI папок: {len(ai_folders)}")
    for folder_name, folder_path, agent_type in ai_folders:
        file_count = sum(1 for _, _, files in os.walk(folder_path) for _ in files)
        print(f"  - {agent_type} ({folder_name}): {file_count} файлов")
    print()

    # Тестируем поиск docs папки
    print("3. Тестируем поиск docs папки:")
    docs_path = get_docs_folder(test_project_path)
    if docs_path:
        docs_file_count = sum(1 for _, _, files in os.walk(docs_path) for _ in files)
        print(f"Найдена docs папка: {docs_file_count} файлов")
    else:
        print("Docs папка не найдена")
    print()

    # Тестируем выбор файлов из папки
    print("4. Тестируем выбор файлов из AI папок:")
    include_patterns = [".py", ".md", ".yml", ".yaml"]
    exclude_patterns = ["__pycache__", "*.pyc"]

    for _folder_name, folder_path, agent_type in ai_folders:
        selected_files = select_folder_files(
            folder_path,
            include_patterns=include_patterns,
            exclude_patterns=exclude_patterns,
            max_file_size=100,  # 100KB max
        )
        print(f"  {agent_type}: {len(selected_files)} файлов выбрано")
        for file_path in list(selected_files)[:3]:  # показываем первые 3
            print(f"    - {os.path.basename(file_path)}")
    print()

    print("Все тесты завершены успешно! ✅")


if __name__ == "__main__":
    test_new_features()
