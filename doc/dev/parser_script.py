import os
import re

# --- НАСТРОЙКИ ---
# Имя исходного файла, который нужно обработать
INPUT_FILE = "raw.md"


# Имена файлов, которые мы ожидаем найти и создать
EXPECTED_FILENAMES = [
    "gap.md",
    "requirements.md",
    "backlog.md",
    "roadmap.md",
    "sprint-plan.md",
    "documentation-maintenance.md",
]
# --- КОНЕЦ НАСТРОЕК ---


def parse_raw_file():
    """
    Основная функция для анализа файла raw.md и создания отдельных файлов.
    """
    print(f"--- Запуск скрипта обработки файла {INPUT_FILE} ---")
    print(f"Текущая рабочая директория: {os.getcwd()}")

    if not os.path.exists(INPUT_FILE):
        print(f"ОШИБКА: Файл '{INPUT_FILE}' не найден в этой папке.")
        print("Пожалуйста, убедитесь, что файл находится рядом со скриптом.")
        return

    with open(INPUT_FILE, encoding="utf-8") as f:
        content = f.read()
    print(
        f"Файл '{INPUT_FILE}' прочитан успешно. Размер содержимого: {len(content)} символов."
    )

    pattern = re.compile(
        r"(`([a-z-]+.md)`|([A-Z][a-zA-Z\s_`]+\(`([a-z-]+.md)`\)))"
        r".*?"
        r"```[Mm]arkdown\n"
        r"(.*?)\n"
        r"```",
        re.DOTALL,
    )

    matches = pattern.findall(content)
    print(f"Найдено {len(matches)} совпадений с regex.")

    if not matches:
        print(
            "ОШИБКА: Не найдено ни одного блока документации в формате ```markdown...```."
        )
        return

    found_count = 0
    for i, match in enumerate(matches):
        print(f"Обработка совпадения {i+1}: {match}")
        filename = next(
            (name for name in [match[1], match[3]] if name and name.endswith(".md")), None
        )
        print(f"Извлечённое имя файла: {filename}")

        if filename and filename in EXPECTED_FILENAMES:
            file_content = match[4].strip()
            print(f"Содержимое файла (первые 100 символов): {file_content[:100]}...")

            print(f"Найден документ: {filename}. Создание файла...")

            # ФИКС: Используем имя файла напрямую, так как сохраняем в той же папке
            full_path = filename
            print(f"Полный путь для сохранения: {full_path}")

            try:
                with open(full_path, "w", encoding="utf-8") as f_out:
                    f_out.write(file_content)
                print(f"  [+] Файл '{full_path}' успешно создан.")
                found_count += 1
            except OSError as e:
                print(f"  [!] ОШИБКА при записи файла '{full_path}': {e}")
        else:
            print(f"Имя файла '{filename}' не найдено в списке ожидаемых или невалидно.")

    print(
        f"--- Завершено. Создано {found_count} из {len(EXPECTED_FILENAMES)} ожидаемых файлов. ---"
    )


if __name__ == "__main__":
    parse_raw_file()
    os.system("pause")
