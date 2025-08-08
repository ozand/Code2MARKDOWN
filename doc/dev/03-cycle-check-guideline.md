# Гайдлайн по скрипту проверки циклических импортов

## Назначение

Скрипт `check-cycles` предназначен для обнаружения циклических импортов в проекте. Циклические импорты могут привести к различным проблемам, включая неочевидное поведение кода, сложности в тестировании и поддержке, а также потенциальные ошибки импорта.

## Как это работает

Скрипт использует инструмент `pydeps` для анализа зависимостей между модулями проекта. Он строит граф импортов и проверяет, есть ли в нем циклы.

## Как запустить

Скрипт интегрирован в CI/CD и автоматически запускается при каждом пуше и создании pull request.

Для ручного запуска используйте команду:

```bash
uv run check-cycles
```

Эта команда запустит точку входа `scripts/check_cycles.py`, которая в свою очередь запустит `scripts/development/__main__.py` с использованием `pydeps`.

## Что делать, если скрипт нашел циклы

Если скрипт обнаружит циклические импорты, CI/CD pipeline завершится с ошибкой. В логах будет указано, между какими модулями обнаружен цикл.

Для исправления проблемы необходимо:

1.  Проанализировать структуру зависимостей между указанными модулями.
2.  Рефакторить код, чтобы разорвать цикл. Это может включать:
    *   Перемещение общего кода в отдельный модуль.
    *   Использование отложенного импорта (import inside function).
    *   Пересмотр архитектуры модулей.
3.  После внесения изменений снова запустить скрипт, чтобы убедиться, что цикл устранен.

## Конфигурация

Скрипт использует стандартные настройки `pydeps`. При необходимости их можно настроить в файле `scripts/development/__main__.py`.

## Код скрипта

### `scripts/check_cycles.py` (точка входа)

```python
"""
Модуль для запуска скрипта проверки циклических импортов.
"""

import subprocess
import sys
from pathlib import Path

def main():
    """Главная функция для запуска скрипта проверки циклических импортов."""
    # Определяем путь к скрипту
    script_path = Path(__file__).parent / "development" / "__main__.py"
    
    if not script_path.exists():
        print(f"Ошибка: Скрипт {script_path} не найден.")
        sys.exit(1)
    
    # Запускаем скрипт
    result = subprocess.run([sys.executable, str(script_path)], check=False)
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()
```

### `scripts/development/__main__.py` (основной скрипт)

```python
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
        sys.executable, "-m", "pydeps",
        "--show-cycles",
        "--no-output",  # Не создавать графические файлы
        str(src_path)
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
```