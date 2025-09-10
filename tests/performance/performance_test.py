#!/usr/bin/env python3
"""
Нагрузочное тестирование производительности приложения Code2MARKDOWN
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path

from code2markdown.application.services import GenerationService
from code2markdown.domain.files import ProjectTreeBuilder
from code2markdown.domain.filters import FileSize, FilterSettings
from code2markdown.infrastructure.database import SqliteHistoryRepository


class PerformanceTester:
    """Класс для проведения нагрузочного тестирования"""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.builder = ProjectTreeBuilder()
        self.filters = FilterSettings(
            include_patterns=[
                ".py",
                ".js",
                ".ts",
                ".md",
                ".txt",
                ".json",
                ".yml",
                ".yaml",
            ],
            exclude_patterns=["__pycache__", ".git", "node_modules", ".venv"],
            max_file_size=FileSize(kb=100),
            max_depth=None,
        )
        self.results: dict = {}

    def count_files(self) -> tuple[int, int]:
        """Подсчитывает количество файлов и директорий в проекте"""
        file_count = 0
        dir_count = 0

        for _root, _dirs, files in os.walk(self.project_path):
            dir_count += len(_dirs)
            file_count += len(files)

        return file_count, dir_count

    def test_tree_building(self) -> dict:
        """Тестирует производительность построения дерева проекта"""
        print("Тестирование построения дерева проекта...")

        start_time = time.time()
        root_node = self.builder.build_tree(str(self.project_path), self.filters)
        end_time = time.time()

        # Подсчитываем количество узлов в дереве
        node_count = self._count_nodes(root_node)

        return {
            "operation": "build_tree",
            "duration": end_time - start_time,
            "node_count": node_count,
            "file_count": self._count_file_nodes(root_node),
            "dir_count": self._count_dir_nodes(root_node),
        }

    def _count_nodes(self, node) -> int:
        """Рекурсивно подсчитывает количество узлов в дереве"""
        if hasattr(node, "children"):
            return 1 + sum(self._count_nodes(child) for child in node.children)
        return 1

    def _count_file_nodes(self, node) -> int:
        """Подсчитывает количество файловых узлов"""
        if hasattr(node, "children"):
            return sum(self._count_file_nodes(child) for child in node.children)
        return 1 if hasattr(node, "size") else 0

    def _count_dir_nodes(self, node) -> int:
        """Подсчитывает количество директорийных узлов"""
        if hasattr(node, "children"):
            return 1 + sum(self._count_dir_nodes(child) for child in node.children)
        return 0

    def test_long_running_stability(self, duration_hours: float = 1) -> dict:
        """Тестирует стабильность при длительной работе"""
        print(
            f"Тестирование стабильности при длительной работе ({duration_hours} час)..."
        )

        start_time = time.time()
        end_time = start_time + (duration_hours * 3600)
        iterations = 0

        try:
            while time.time() < end_time:
                # Периодически строим дерево проекта
                self.builder.build_tree(str(self.project_path), self.filters)
                iterations += 1

                # Делаем небольшую паузу, чтобы имитировать реальную нагрузку
                time.sleep(0.1)

                # Выводим прогресс каждые 100 итераций
                if iterations % 100 == 0:
                    print(f"  Выполнено итераций: {iterations}")

        except (OSError, ValueError, TypeError) as e:
            return {
                "operation": "long_running_stability",
                "status": "failed",
                "error": str(e),
                "iterations": iterations,
                "duration": time.time() - start_time,
            }

        return {
            "operation": "long_running_stability",
            "status": "success",
            "iterations": iterations,
            "duration": time.time() - start_time,
        }

    def test_ui_response_time(self) -> dict:
        """Тестирует время отклика UI"""
        print("Тестирование времени отклика UI...")

        # Создаем сервис для генерации документации
        repo = SqliteHistoryRepository()
        service = GenerationService(repo)

        # Тестируем генерацию документации
        start_time = time.time()
        try:
            markdown_content = service.generate_and_save_documentation(
                project_path=str(self.project_path),
                template_name="default_template.hbs",
                filters=self.filters,
            )
            success = True
            error = None
        except (ValueError, TypeError, OSError) as e:
            success = False
            error = str(e)
            markdown_content = None

        end_time = time.time()

        return {
            "operation": "ui_response_time",
            "duration": end_time - start_time,
            "success": success,
            "error": error,
            "content_length": len(markdown_content) if markdown_content else 0,
        }

    def run_all_tests(self) -> dict:
        """Запускает все тесты и возвращает результаты"""
        print(f"Запуск нагрузочного тестирования для проекта: {self.project_path}")
        print(f"Время начала: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Подсчитываем файлы
        total_files, total_dirs = self.count_files()
        print(f"Общее количество файлов: {total_files}")
        print(f"Общее количество директорий: {total_dirs}")

        # Запускаем тесты
        results: dict[str, object | list[dict[str, object]]] = {
            "project_path": str(self.project_path),
            "total_files": total_files,
            "total_dirs": total_dirs,
            "test_start_time": datetime.now().isoformat(),
            "tests": [],
        }
        tests_list: list[dict[str, object]] = results["tests"]  # type: ignore

        # Тест построения дерева
        tree_result = self.test_tree_building()
        if isinstance(tests_list, list):
            tests_list.append(tree_result)
        print(f"  Время построения дерева: {tree_result['duration']:.3f} сек")

        # Тест стабильности
        stability_result = self.test_long_running_stability(
            duration_hours=0.1
        )  # Уменьшаем время для тестирования
        if isinstance(tests_list, list):
            tests_list.append(stability_result)
        print(f"  Стабильность: {stability_result['status']}")

        # Тест времени отклика UI
        ui_result = self.test_ui_response_time()
        if isinstance(tests_list, list):
            tests_list.append(ui_result)
        print(f"  Время отклика UI: {ui_result['duration']:.3f} сек")

        results["test_end_time"] = datetime.now().isoformat()
        results["total_duration"] = sum(
            test["duration"]
            for test in tests_list
            if isinstance(test, dict)
            and "duration" in test
            and isinstance(test["duration"], int | float)
        )

        # Сохраняем результаты
        self.save_results(results)

        return results

    def save_results(self, results: dict):
        """Сохраняет результаты тестирования в файл"""
        results_dir = Path("test_results")
        results_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = results_dir / f"performance_test_{timestamp}.json"

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        print(f"\nРезультаты тестирования сохранены в: {filename}")

        # Печатаем сводку
        self.print_summary(results)

    def print_summary(self, results: dict):
        """Печатает сводку результатов тестирования"""
        print("\n" + "=" * 50)
        print("СВОДКА РЕЗУЛЬТАТОВ НАГРУЗОЧНОГО ТЕСТИРОВАНИЯ")
        print("=" * 50)

        print(f"Проект: {results['project_path']}")
        print(f"Файлов: {results['total_files']}")
        print(f"Директорий: {results['total_dirs']}")
        print(f"Общее время тестирования: {results['total_duration']:.3f} сек")

        for test in results["tests"]:
            if test["operation"] == "build_tree":
                print("\nПостроение дерева:")
                print(f"  Время: {test['duration']:.3f} сек")
                print(f"  Узлов: {test['node_count']}")
                print(f"  Файлов: {test['file_count']}")
                print(f"  Директорий: {test['dir_count']}")

            elif test["operation"] == "long_running_stability":
                print("\nСтабильность при длительной работе:")
                print(f"  Статус: {test['status']}")
                print(f"  Итераций: {test['iterations']}")
                print(f"  Длительность: {test['duration']:.3f} сек")

            elif test["operation"] == "ui_response_time":
                print("\nВремя отклика UI:")
                print(f"  Время: {test['duration']:.3f} сек")
                print(f"  Успешно: {test['success']}")
                if test["error"]:
                    print(f"  Ошибка: {test['error']}")
                print(f"  Длина контента: {test['content_length']} символов")


def main():
    """Основная функция для запуска тестирования"""
    # Используем директорию с большим количеством файлов для тестирования
    project_path = Path("test_large_project")

    if not project_path.exists():
        print(f"Директория {project_path} не найдена!")
        print("Создаем тестовую директорию с большим количеством файлов...")

        # Создаем директорию для тестов
        project_path.mkdir(exist_ok=True)

        # Создаем много файлов для тестирования
        for i in range(100):  # Создаем 100 директорий
            dir_path = project_path / f"dir{i:02d}"
            dir_path.mkdir(exist_ok=True)

            # В каждой директории создаем 50 файлов
            for j in range(50):
                file_path = dir_path / f"file{j:02d}.py"
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(
                        f"""# Тестовый файл {i:02d}_{j:02d}\n\n"""
                        f"""def test_function_{j}():\n"""
                        f"""    \"\"\"Тестовая функция {j}\"\"\"\n"""
                        f"""    result = 0\n"""
                        f"""    for k in range(100):\n"""
                        f"""        result += k * 2\n"""
                        f"""    return result\n\n"""
                        f"""if __name__ == "__main__":\n"""
                        f"""    print(f"Результат: {{test_function_{j}()}}")\n"""
                    )

        print(f"Создано {100*50} тестовых файлов для нагрузочного тестирования")

    # Запускаем тестирование
    tester = PerformanceTester(str(project_path))
    results = tester.run_all_tests()

    return results


if __name__ == "__main__":
    main()
