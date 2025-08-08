#!/usr/bin/env python3
"""
Скрипт для проверки циклических импортов в проекте с использованием pydeps.

Этот скрипт использует pydeps для анализа зависимостей в проекте
и поиска циклических импортов.

Использование:
    python scripts/development/check_cycles.py
"""

import subprocess
import sys
from pathlib import Path


def check_cycles():
    """
    Проверяет циклические импорты в проекте.

    Returns:
        bool: True, если циклы не найдены, False в противном случае.
    """
    # Определяем путь к исходному коду
    src_path = Path("src")

    if not src_path.exists():
        print(f"Ошибка: Директория {src_path} не найдена.")
        return False

    # Команда для запуска pydeps с флагом --show-cycles
    cmd = [
        sys.executable,
        "-m",
        "pydeps",
        "--show-cycles",
        "--no-output",  # Не создавать графические файлы
        str(src_path),
    ]

    try:
        # Запускаем pydeps
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)

        # Выводим результат
        if result.stdout:
            print("Найдены циклические импорты:")
            print(result.stdout)
            return False
        else:
            print("Циклические импорты не найдены.")
            return True

    except FileNotFoundError:
        print("Ошибка: pydeps не найден. Убедитесь, что он установлен.")
        return False
    except Exception as e:
        print(f"Ошибка при выполнении pydeps: {e}")
        return False


def main():
    """Главная функция скрипта."""
    success = check_cycles()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
