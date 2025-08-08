"""
Модуль для запуска скрипта проверки циклических импортов.
"""

import subprocess
import sys
from pathlib import Path


def main():
    """Главная функция для запуска скрипта проверки циклических импортов."""
    # Определяем путь к скрипту
    script_path = Path(__file__).parent.parent / "scripts" / "development" / "__main__.py"

    if not script_path.exists():
        print(f"Ошибка: Скрипт {script_path} не найден.")
        sys.exit(1)

    # Запускаем скрипт
    result = subprocess.run([sys.executable, str(script_path)], check=False)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
