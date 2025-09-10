#!/usr/bin/env python3
"""
Скрипт для Валидации Базы Знаний (Knowledge Base)

Этот скрипт проверяет целостность базы знаний Logseq согласно правилам,
определенным в стандарте проекта. Он реализует следующие проверки:
  1.  **Целостность ссылок:** Убеждается, что все ссылки `[[...]]` в файлах
      указывают на существующие страницы (.md файлы). При этом ссылки в
      блоках кода (fenced ```...``` и inline `...`) игнорируются для
      предотвращения ложных срабатываний.
  2.  **Правильное форматирование ссылок:** Проверяет, что все ссылки на
      внешние файлы (код, тесты) следуют формату с алиасом `[[path|`file`]]`.
      Ссылки в блоках кода также игнорируются.
  3.  **Структура файлов:** Проверяет, что все документы созданы в правильных
      директориях и следуют соглашениям по именованию.
  4.  **Схема свойств:** Проверяет, что все User Stories и Requirements имеют
      обязательные свойства.
  5.  **Правильность статусов:** Проверяет, что значения свойства status
      соответствуют разрешенному списку.
  6.  **Целостность заголовков в README:** Проверяет, что все README.md файлы
      имеют свойство title::.
  7.  **Обработка временных артефактов:** Проверяет, что файлы с "сырыми"
      выводами команд не сохраняются в pages/.

Для игнорирования ссылок в блоках кода используется вспомогательная функция
`_remove_code_blocks`, которая удаляет как fenced code blocks (```...```), так
и inline code blocks (`...`) из содержимого markdown перед извлечением ссылок.
Это позволяет избежать ложных срабатываний при проверке ссылок в примерах кода
в файлах правил.

Использование:
    python scripts/development/validate_kb.py
"""

import argparse
import re
import sys
from pathlib import Path

# --- Конфигурация ---

# Директории, которые являются частью базы знаний и подлежат сканированию.
KNOWLEDGE_BASE_DIRS = {"pages", "journals"}

# Разрешенные файлы в корне проекта
ALLOWED_ROOT_FILES = {"README.md", "CONTRIBUTING.md"}

# Ссылки, которые нужно игнорировать при проверке, так как они не являются файлами.
# (например, статусы, теги, свойства).
IGNORED_LINKS = {
    "TODO",
    "DOING",
    "DONE",  # Статусы задач
    "high",
    "medium",
    "low",  # Приоритеты
    "story",
    "requirement",
    "implementation-plan",  # Типы документов
    "PLANNED",
    "IMPLEMENTED",
    "PARTIAL",  # Статусы требований
    "DRAFT",
    "APPROVED",
    "COMPLETED",  # Статусы планов
}


class KBValidator:
    """Валидатор Базы Знаний, реализующий все проверки."""

    def __init__(self, base_path: Path):
        self.base_path = base_path.resolve()
        self.errors: list[str] = []
        self.warnings: list[str] = []
        # Регулярное выражение для поиска всех ссылок [[...]]
        self.link_pattern = re.compile(r"\[\[([^\]]+)\]\]")
        # Регулярные выражения для проверки имен файлов
        self.story_pattern = re.compile(r"^STORY-[A-Z]+-\d+\.md$")
        self.req_pattern = re.compile(r"^REQ-[A-Z]+-\d+\.md$")
        self.rule_pattern = re.compile(r"^\.roo/rules/[^/]+\.md$")
        # Регулярное выражение для поиска ссылок с алиасами
        self.alias_link_pattern = re.compile(r"\[\[([^\]|]+)\|`([^`]+)`\]\]")
        # Загружаем паттерны из .gitignore
        self.gitignore_patterns = self._load_gitignore()

    def _load_gitignore(self) -> list[str]:
        """Загружает и парсит паттерны из .gitignore."""
        gitignore_path = self.base_path / ".gitignore"
        patterns = []

        if gitignore_path.exists():
            try:
                with open(gitignore_path, encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        # Пропускаем пустые строки и комментарии
                        if line and not line.startswith("#"):
                            patterns.append(line)
            except OSError as e:
                self.warnings.append(f"Не удалось прочитать .gitignore: {e}")

        return patterns

    def _is_ignored(self, file_path: Path) -> bool:
        """Проверяет, игнорируется ли файл по паттернам из .gitignore."""
        try:
            relative_path = file_path.relative_to(self.base_path).as_posix()

            for pattern in self.gitignore_patterns:
                # Преобразуем паттерн в регулярное выражение
                # Это упрощенная реализация, не охватывает все случаи gitignore
                regex_pattern = (
                    pattern.replace(".", "\\.").replace("*", ".*").replace("?", ".?")
                )

                # Если паттерн заканчивается на /, это директория
                if pattern.endswith("/"):
                    regex_pattern = regex_pattern.rstrip("/") + "/.*"

                # Компилируем регулярное выражение
                try:
                    if re.match(regex_pattern, relative_path) or re.match(
                        regex_pattern, relative_path + "/"
                    ):
                        return True
                except re.error:
                    # Игнорируем некорректные регулярные выражения
                    continue
        except ValueError:
            # Если не удалось получить относительный путь, считаем файл не игнорируемым
            pass

        return False

    def _remove_code_blocks(self, content: str) -> str:
        """Удаляет блоки кода из содержимого markdown перед проверкой ссылок."""
        # Удаляем fenced code blocks (```...```)
        fenced_pattern = re.compile(r"```.*?```", re.DOTALL)
        content_without_fenced = re.sub(fenced_pattern, "", content)

        # Удаляем inline code blocks (`...`)
        inline_pattern = re.compile(r"`[^`]*`")
        content_without_code = re.sub(inline_pattern, "", content_without_fenced)

        return content_without_code

    def _find_markdown_files(self) -> list[Path]:
        """Находит все .md файлы, рекурсивно сканируя директории из KNOWLEDGE_BASE_DIRS."""
        markdown_files = []
        print("Сканирование директорий базы знаний:")
        for kb_dir_name in KNOWLEDGE_BASE_DIRS:
            kb_dir_path = self.base_path / kb_dir_name
            if kb_dir_path.is_dir():
                print(f"  - Сканирую '{kb_dir_name}'...")
                files_in_dir = list(kb_dir_path.rglob("*.md"))
                # Фильтруем файлы, игнорируемые по .gitignore
                filtered_files = [f for f in files_in_dir if not self._is_ignored(f)]
                markdown_files.extend(filtered_files)
            else:
                self.warnings.append(
                    f"Директория '{kb_dir_name}' не найдена и была пропущена."
                )

        # Также добавляем файлы из .roo/rules/
        rules_dir_path = self.base_path / ".roo/rules"
        if rules_dir_path.is_dir():
            print("  - Сканирую '.roo/rules'...")
            rules_files = list(rules_dir_path.rglob("*.md"))
            # Фильтруем файлы, игнорируемые по .gitignore
            filtered_rules_files = [f for f in rules_files if not self._is_ignored(f)]
            markdown_files.extend(filtered_rules_files)
        else:
            self.warnings.append("Директория '.roo/rules' не найдена и была пропущена.")

        return markdown_files

    def _get_all_page_names(self, all_md_files: list[Path]) -> set[str]:
        """Создает множество всех существующих имен страниц из имен файлов."""
        # Имя страницы - это имя файла без расширения .md
        return {file.stem for file in all_md_files}

    def validate_link_integrity(self, md_file: Path, all_pages: set[str]):
        """Проверяет все ссылки в одном файле на существование."""
        try:
            content = md_file.read_text(encoding="utf-8")
            # Удаляем блоки кода перед извлечением ссылок
            content_without_code = self._remove_code_blocks(content)
            found_links = self.link_pattern.findall(content_without_code)

            for link in found_links:
                # Игнорируем ссылки с алиасами или пути к файлам
                if "|" in link or "/" in link or "\\" in link:
                    continue

                # Игнорируем специальные ссылки из списка IGNORED_LINKS
                if link in IGNORED_LINKS:
                    continue

                # Проверяем, существует ли страница для данной ссылки
                if link not in all_pages:
                    relative_path = md_file.relative_to(self.base_path)
                    self.errors.append(
                        f"Broken link in '{relative_path}': [[{link}]] points to a non-existent page."
                    )

        except (OSError, UnicodeDecodeError) as e:
            self.warnings.append(f"Could not read or process file '{md_file}': {e}")

    def validate_correct_link_formatting(self, md_file: Path):
        """Проверяет, что ссылки на внешние файлы следуют правильному формату алиасов."""
        try:
            content = md_file.read_text(encoding="utf-8")
            # Удаляем блоки кода перед извлечением ссылок
            content_without_code = self._remove_code_blocks(content)
            # Находим все ссылки с алиасами
            found_alias_links = self.alias_link_pattern.findall(content_without_code)

            for path, filename in found_alias_links:
                # Проверяем, что имя файла в алиасе соответствует фактическому имени файла в пути
                # Например, [[path/to/file.py|`file.py`]] - здесь filename должно быть file.py
                actual_filename = Path(path).name
                if filename != actual_filename:
                    relative_path = md_file.relative_to(self.base_path)
                    self.errors.append(
                        f"Incorrect alias format in '{relative_path}': [[{path}|`{filename}`]] should be [[{path}|`{actual_filename}`]]"
                    )

                # Проверяем, что путь указывает на существующий файл (если это локальный путь)
                if not path.startswith("http") and not path.startswith("https"):
                    # Для локальных путей проверяем, что файл существует
                    path_obj = Path(path)
                    # Если путь относительный, проверяем относительно корня проекта
                    if not path_obj.is_absolute():
                        full_path = self.base_path / path_obj
                        if not full_path.exists():
                            relative_path = md_file.relative_to(self.base_path)
                            self.errors.append(
                                f"Link to non-existent file in '{relative_path}': [[{path}|`{filename}`]] points to a non-existent file."
                            )

        except (OSError, UnicodeDecodeError) as e:
            self.warnings.append(
                f"Could not validate link formatting for '{md_file}': {e}"
            )

    def validate_file_structure(self, md_file: Path):
        """Проверяет структуру файлов и соглашения по именованию."""
        try:
            relative_path = md_file.relative_to(self.base_path).as_posix()

            # Проверка User Stories
            if relative_path.startswith("pages/") and relative_path.endswith(".md"):
                filename = Path(relative_path).name
                if filename.startswith("STORY-"):
                    if not self.story_pattern.match(filename):
                        self.errors.append(
                            f"Неправильное имя файла User Story: '{relative_path}'. Должно быть в формате STORY-[CATEGORY]-[ID].md"
                        )

            # Проверка Requirements
            if relative_path.startswith("pages/") and relative_path.endswith(".md"):
                filename = Path(relative_path).name
                if filename.startswith("REQ-"):
                    if not self.req_pattern.match(filename):
                        self.errors.append(
                            f"Неправильное имя файла Requirement: '{relative_path}'. Должно быть в формате REQ-[CATEGORY]-[ID].md"
                        )

            # Проверка Rules (для файлов в .roo/rules/)
            if relative_path.startswith(".roo/rules/") and relative_path.endswith(".md"):
                # Проверка, что файлы правил находятся непосредственно в .roo/rules/, а не в поддиректориях
                path_parts = Path(relative_path).parts
                if len(path_parts) != 3:  # .roo/rules/filename.md
                    self.errors.append(
                        f"Файл правила должен находиться непосредственно в .roo/rules/: '{relative_path}'"
                    )

        except Exception as e:
            self.warnings.append(
                f"Could not validate file structure for '{md_file}': {e}"
            )

    def validate_properties_schema(self, md_file: Path):
        """Проверяет, что User Stories и Requirements имеют обязательные свойства."""
        try:
            relative_path = md_file.relative_to(self.base_path).as_posix()
            filename = Path(relative_path).name

            # Проверяем только файлы в директории pages
            if not relative_path.startswith("pages/"):
                return

            content = md_file.read_text(encoding="utf-8")

            # Проверка User Stories
            if filename.startswith("STORY-"):
                # Проверяем наличие всех обязательных свойств User Story
                required_properties = [
                    "type:: [[story]]",
                    "status::",
                    "priority::",
                    "assignee::",
                    "epic::",
                    "related-reqs::",
                ]

                missing_properties = []
                for prop in required_properties:
                    if prop not in content:
                        missing_properties.append(prop)

                if missing_properties:
                    self.errors.append(
                        f"User Story '{relative_path}' отсутствуют обязательные свойства: {', '.join(missing_properties)}"
                    )

            # Проверка Requirements
            elif filename.startswith("REQ-"):
                # Проверяем наличие всех обязательных свойств Requirement
                required_properties = ["type:: [[requirement]]", "status::"]

                missing_properties = []
                for prop in required_properties:
                    if prop not in content:
                        missing_properties.append(prop)

                if missing_properties:
                    self.errors.append(
                        f"Requirement '{relative_path}' отсутствуют обязательные свойства: {', '.join(missing_properties)}"
                    )

        except (OSError, UnicodeDecodeError) as e:
            self.warnings.append(
                f"Could not validate properties schema for '{md_file}': {e}"
            )

    def validate_status_correctness(self, md_file: Path):
        """Проверяет, что значения свойства status соответствуют разрешенному списку."""
        try:
            relative_path = md_file.relative_to(self.base_path).as_posix()
            filename = Path(relative_path).name

            # Проверяем только файлы в директории pages
            if not relative_path.startswith("pages/"):
                return

            content = md_file.read_text(encoding="utf-8")

            # Проверка User Stories
            if filename.startswith("STORY-"):
                # Найдем строку со статусом
                status_line = None
                for line in content.split("\n"):
                    if line.startswith("status::"):
                        status_line = line
                        break

                if status_line:
                    # Проверяем, что статус соответствует разрешенному списку
                    allowed_statuses = ["[[TODO]]", "[[DOING]]", "[[DONE]]"]
                    status_value = status_line.split("status::", 1)[1].strip()
                    if status_value not in allowed_statuses:
                        self.errors.append(
                            f"User Story '{relative_path}' имеет недопустимый статус: '{status_value}'. Допустимые значения: {', '.join(allowed_statuses)}"
                        )

            # Проверка Requirements
            elif filename.startswith("REQ-"):
                # Найдем строку со статусом
                status_line = None
                for line in content.split("\n"):
                    if line.startswith("status::"):
                        status_line = line
                        break

                if status_line:
                    # Проверяем, что статус соответствует разрешенному списку
                    allowed_statuses = ["[[PLANNED]]", "[[IMPLEMENTED]]", "[[PARTIAL]]"]
                    status_value = status_line.split("status::", 1)[1].strip()
                    if status_value not in allowed_statuses:
                        self.errors.append(
                            f"Requirement '{relative_path}' имеет недопустимый статус: '{status_value}'. Допустимые значения: {', '.join(allowed_statuses)}"
                        )

        except (OSError, UnicodeDecodeError) as e:
            self.warnings.append(
                f"Could not validate status correctness for '{md_file}': {e}"
            )

    def validate_readme_title(self, md_file: Path):
        """Проверяет, что все README.md файлы имеют свойство title::."""
        try:
            relative_path = md_file.relative_to(self.base_path).as_posix()
            filename = Path(relative_path).name

            # Проверяем только файлы с именем README.md
            if filename == "README.md":
                content = md_file.read_text(encoding="utf-8")

                # Проверяем наличие свойства title::
                if "title::" not in content:
                    self.errors.append(
                        f"README.md файл '{relative_path}' не имеет свойства 'title::'"
                    )

        except Exception as e:
            self.warnings.append(f"Could not validate README title for '{md_file}': {e}")

    def validate_temporary_artifacts(self, md_file: Path):
        """Проверяет, что файлы с 'сырыми' выводами команд не сохраняются в pages/."""
        try:
            relative_path = md_file.relative_to(self.base_path).as_posix()
            filename = Path(relative_path).name

            # Проверяем только файлы в директории pages
            if not relative_path.startswith("pages/"):
                return

            # Проверяем файлы, которые являются "сырыми" выводами команд
            # Примеры: raw.md, error.errors
            raw_command_output_patterns = ["raw.md", "error.errors"]

            if filename in raw_command_output_patterns:
                self.errors.append(
                    f"Файл '{relative_path}' является временным артефактом и не должен сохраняться в pages/"
                )

        except (OSError, UnicodeDecodeError) as e:
            self.warnings.append(
                f"Could not validate temporary artifacts for '{md_file}': {e}"
            )

    def validate_misplaced_files(self):
        """Проверяет, что markdown файлы находятся в разрешенных директориях."""
        try:
            # Сканируем все markdown файлы в проекте
            all_md_files = list(self.base_path.rglob("*.md"))

            # Фильтруем файлы, игнорируемые по .gitignore
            all_md_files = [f for f in all_md_files if not self._is_ignored(f)]

            for md_file in all_md_files:
                try:
                    relative_path = md_file.relative_to(self.base_path).as_posix()

                    # Проверяем, находится ли файл в разрешенной директории
                    is_in_allowed_dir = any(
                        relative_path.startswith(allowed_dir + "/")
                        for allowed_dir in KNOWLEDGE_BASE_DIRS
                    )

                    # Проверяем, является ли файл разрешенным в корне
                    is_allowed_root_file = relative_path in ALLOWED_ROOT_FILES

                    # Проверяем, находится ли файл в .roo/rules/
                    is_in_rules_dir = relative_path.startswith(".roo/rules/")

                    # Файл разрешен, если он в одной из разрешенных директорий
                    # или является разрешенным файлом в корне
                    if not (is_in_allowed_dir or is_allowed_root_file or is_in_rules_dir):
                        self.errors.append(
                            f"Файл '{relative_path}' находится вне разрешенных директорий. "
                            f"Разрешенные директории: {', '.join(KNOWLEDGE_BASE_DIRS)}, .roo/rules/, "
                            f"разрешенные файлы в корне: {', '.join(ALLOWED_ROOT_FILES)}"
                        )
                except ValueError:
                    # Если не удалось получить относительный путь, пропускаем файл
                    continue
        except (OSError, RuntimeError) as e:
            self.warnings.append(f"Не удалось выполнить проверку misplaced files: {e}")

    def run_validation(self):
        """Запускает все проверки для базы знаний."""
        print(f"Корень проекта: {self.base_path}")
        all_md_files = self._find_markdown_files()

        if not all_md_files:
            self.warnings.append("Не найдено ни одного markdown-файла для валидации.")
            return

        print(f"\nНайдено {len(all_md_files)} файлов. Собираю имена всех страниц...")
        all_page_names = self._get_all_page_names(all_md_files)

        print("Запуск валидации целостности ссылок...")
        for md_file in all_md_files:
            self.validate_link_integrity(md_file, all_page_names)

        print("Запуск валидации правильного форматирования ссылок...")
        for md_file in all_md_files:
            self.validate_correct_link_formatting(md_file)

        print("Запуск валидации структуры файлов...")
        for md_file in all_md_files:
            self.validate_file_structure(md_file)

        print("Запуск валидации схемы свойств...")
        for md_file in all_md_files:
            self.validate_properties_schema(md_file)

        print("Запуск валидации правильности статусов...")
        for md_file in all_md_files:
            self.validate_status_correctness(md_file)

        print("Запуск валидации заголовков в README...")
        for md_file in all_md_files:
            self.validate_readme_title(md_file)

        print("Запуск валидации временных артефактов...")
        for md_file in all_md_files:
            self.validate_temporary_artifacts(md_file)

        print("Запуск валидации misplaced файлов...")
        self.validate_misplaced_files()

        print("Валидация завершена.")

    def print_report(self):
        """Выводит итоговый отчет о найденных ошибках и предупреждениях."""
        print("\n--- Отчет о валидации ---")
        if not self.errors and not self.warnings:
            print("\n✅ Все проверки успешно пройдены! Ошибок не найдено.")
            return

        if self.warnings:
            print(f"\n⚠️  Найдено предупреждений: {len(self.warnings)}")
            for warning in self.warnings:
                print(f"  - {warning}")

        if self.errors:
            print(f"\n❌ Найдено ошибок: {len(self.errors)}")
            for error in self.errors:
                print(f"  - {error}")

        print("\n-------------------------")


def main():
    parser = argparse.ArgumentParser(
        description="Скрипт для Валидации Базы Знаний Logseq."
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="Корневая директория проекта для валидации.",
    )
    args = parser.parse_args()

    validator = KBValidator(args.project_root)
    validator.run_validation()
    validator.print_report()

    if validator.errors:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
