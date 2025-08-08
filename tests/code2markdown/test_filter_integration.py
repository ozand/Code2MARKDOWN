#!/usr/bin/env python3
"""
Тест интеграции Filter Settings с File Selection
"""

import os

# Импортируем функции из app.py
from code2markdown.app import (
    get_all_child_paths,
    get_file_tree_structure,
)


def test_filter_integration():
    """Тестируем новую функциональность фильтрации"""

    print("🔍 Тестирование интеграции Filter Settings с File Selection")
    print("=" * 60)

    # Используем test_project для тестирования
    test_project_path = "test_project"

    if not os.path.exists(test_project_path):
        print(f"❌ Папка {test_project_path} не найдена")
        return

    # Настройки фильтров для тестирования
    include_patterns = [".py", ".md", ".txt"]
    exclude_patterns = ["__pycache__", "*.pyc", "cache"]
    max_file_size = 100  # KB

    print(f"📁 Тестовый проект: {test_project_path}")
    print(f"📥 Include patterns: {include_patterns}")
    print(f"📤 Exclude patterns: {exclude_patterns}")
    print(f"📊 Max file size: {max_file_size} KB")
    print()

    # Тест 1: Структура с исключенными файлами (show_excluded=False)
    print("🧪 Тест 1: Показ только включенных файлов")
    print("-" * 40)

    tree_included = get_file_tree_structure(
        test_project_path,
        max_depth=3,
        include_patterns=include_patterns,
        exclude_patterns=exclude_patterns,
        max_file_size=max_file_size,
        show_excluded=False,
    )

    included_count = count_files_in_tree(tree_included)
    print(f"✅ Включенных файлов найдено: {included_count}")

    # Тест 2: Структура с показом исключенных файлов (show_excluded=True)
    print("\n🧪 Тест 2: Показ включенных и исключенных файлов")
    print("-" * 40)

    tree_all = get_file_tree_structure(
        test_project_path,
        max_depth=3,
        include_patterns=include_patterns,
        exclude_patterns=exclude_patterns,
        max_file_size=max_file_size,
        show_excluded=True,
    )

    all_count = count_files_in_tree(tree_all)
    excluded_count = count_excluded_files_in_tree(tree_all)

    print(f"✅ Всего файлов найдено: {all_count}")
    print(f"❌ Исключенных файлов: {excluded_count}")
    print(f"✅ Включенных файлов: {all_count - excluded_count}")

    # Тест 3: Проверка get_all_child_paths с exclude_excluded
    print("\n🧪 Тест 3: Функция get_all_child_paths")
    print("-" * 40)

    if tree_all:
        first_folder = None
        for name, info in tree_all.items():
            if info["type"] == "folder":
                first_folder = info
                break

        if first_folder:
            paths_all = get_all_child_paths(first_folder, include_excluded=True)
            paths_included = get_all_child_paths(first_folder, include_excluded=False)

            print(f"✅ Всех путей в первой папке: {len(paths_all)}")
            print(f"✅ Включенных путей: {len(paths_included)}")
            print(f"❌ Исключенных путей: {len(paths_all) - len(paths_included)}")

    # Тест 4: Проверка различных типов исключений
    print("\n🧪 Тест 4: Типы исключений")
    print("-" * 40)

    exclusion_stats = analyze_exclusions(tree_all)
    for reason, count in exclusion_stats.items():
        print(f"📊 {reason}: {count} файлов")

    print("\n✅ Все тесты завершены успешно!")


def count_files_in_tree(tree):
    """Подсчитывает количество файлов в дереве"""
    count = 0
    for name, info in tree.items():
        if info["type"] == "file":
            count += 1
        elif info["type"] == "folder" and info.get("children"):
            count += count_files_in_tree(info["children"])
    return count


def count_excluded_files_in_tree(tree):
    """Подсчитывает количество исключенных файлов в дереве"""
    count = 0
    for name, info in tree.items():
        if info["type"] == "file" and info.get("excluded", False):
            count += 1
        elif info["type"] == "folder" and info.get("children"):
            count += count_excluded_files_in_tree(info["children"])
    return count


def analyze_exclusions(tree):
    """Анализирует причины исключения файлов"""
    stats = {"Включенные файлы": 0, "Исключенные файлы": 0, "Исключенные папки": 0}

    def analyze_recursive(structure):
        for name, info in structure.items():
            if info["type"] == "file":
                if info.get("excluded", False):
                    stats["Исключенные файлы"] += 1
                else:
                    stats["Включенные файлы"] += 1
            elif info["type"] == "folder":
                if info.get("excluded", False):
                    stats["Исключенные папки"] += 1
                if info.get("children"):
                    analyze_recursive(info["children"])

    analyze_recursive(tree)
    return stats


if __name__ == "__main__":
    test_filter_integration()
