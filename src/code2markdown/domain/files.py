import fnmatch
import hashlib
import json
import os
from dataclasses import dataclass, field
from typing import Union

import pathspec

from code2markdown.domain.filters import FilterSettings


@dataclass
class FileNode:
    path: str
    name: str
    size: int
    is_binary: bool
    content: str | None = None

    def is_excluded(self, filters: FilterSettings) -> bool:
        """
        Проверяет, должен ли файл быть исключен на основе настроек фильтрации.

        Args:
            filters: Настройки фильтрации

        Returns:
            True если файл должен быть исключен, False в противном случае
        """
        # Проверка по расширению .gitignore
        gitignore_path = os.path.join(os.path.dirname(self.path), ".gitignore")
        try:
            if os.path.exists(gitignore_path):
                with open(gitignore_path, encoding="utf-8") as f:
                    lines = f.readlines()
                spec = pathspec.PathSpec.from_lines("gitwildmatch", lines)
                if spec.match_file(self.path):
                    return True
        except FileNotFoundError:
            # Если файл .gitignore не найден, пропускаем его
            pass

        # Проверка размера файла
        if filters.max_file_size and self.size > filters.max_file_size.bytes:
            return True

        # Проверка include patterns
        if filters.include_patterns:
            filename = os.path.basename(self.path)
            file_ext = os.path.splitext(filename)[1].lower()
            should_include = False

            for pattern in filters.include_patterns:
                pattern = pattern.strip()
                if not pattern:
                    continue
                # Если паттерн начинается с точки - это расширение
                if pattern.startswith("."):
                    if file_ext == pattern.lower():
                        should_include = True
                        break
                # Если содержит звездочку - это wildcard паттерн
                elif "*" in pattern:
                    if fnmatch.fnmatch(filename.lower(), pattern.lower()):
                        should_include = True
                        break
                # Иначе проверяем вхождение в имя файла
                else:
                    if pattern.lower() in filename.lower():
                        should_include = True
                        break

            if not should_include:
                return True

        # Проверка exclude patterns
        if filters.exclude_patterns:
            filename = os.path.basename(self.path)

            for pattern in filters.exclude_patterns:
                pattern = pattern.strip()
                if not pattern:
                    continue
                # Если содержит звездочку - это wildcard паттерн
                if "*" in pattern:
                    if fnmatch.fnmatch(filename.lower(), pattern.lower()):
                        return True
                # Иначе проверяем вхождение
                else:
                    if pattern.lower() in filename.lower():
                        return True

        return False


@dataclass
class DirectoryNode:
    path: str
    name: str
    children: list[Union["DirectoryNode", "FileNode"]] = field(default_factory=list)

    def is_excluded(self, filters: FilterSettings) -> bool:
        """
        Проверяет, должна ли директория быть исключена на основе настроек фильтрации.

        Args:
            filters: Настройки фильтрации

        Returns:
            True если директория должна быть исключена, False в противном случае
        """
        # Проверка по расширению .gitignore
        gitignore_path = os.path.join(self.path, ".gitignore")
        try:
            if os.path.exists(gitignore_path):
                with open(gitignore_path, encoding="utf-8") as f:
                    lines = f.readlines()
                spec = pathspec.PathSpec.from_lines("gitwildmatch", lines)
                if spec.match_file(self.path):
                    return True
        except FileNotFoundError:
            # Если файл .gitignore не найден, пропускаем его
            pass

        # Проверка exclude patterns
        if filters.exclude_patterns:
            # Используем только имя директории для проверки паттернов
            dir_name = os.path.basename(self.path)

            for pattern in filters.exclude_patterns:
                pattern = pattern.strip()
                if not pattern:
                    continue

                # Удаляем trailing slash из паттерна если есть
                pattern = pattern.rstrip("/")

                # Если паттерн заканчивается на /, проверяем только директории
                is_dir_pattern = pattern.endswith("/")
                if is_dir_pattern:
                    pattern = pattern[:-1]

                # Если содержит звездочку - это wildcard паттерн
                if "*" in pattern:
                    if fnmatch.fnmatch(dir_name.lower(), pattern.lower()):
                        return True
                # Иначе проверяем вхождение
                elif pattern.lower() in dir_name.lower():
                    return True

        return False


class ProjectTreeBuilder:
    """
    Класс для построения дерева проекта с применением фильтров.
    """

    def __init__(self):
        self._cache: dict[str, DirectoryNode | None] = {}
        self._cache_stats = {"hits": 0, "misses": 0}
        # Initialize caches for methods that previously used lru_cache
        self._file_stat_cache: dict[str, tuple[bool, int]] = {}
        self._is_binary_file_cache: dict[str, bool] = {}

    def _get_cache_key(
        self, root_path: str, filters: FilterSettings, current_depth: int = 0
    ) -> str:
        """
        Генерирует уникальный ключ для кэширования на основе параметров.
        """
        filters_data = {
            "include_patterns": sorted(filters.include_patterns or []),
            "exclude_patterns": sorted(filters.exclude_patterns or []),
            "max_file_size": filters.max_file_size.bytes if filters.max_file_size else 0,
            "max_depth": filters.max_depth,
        }
        cache_data = (
            f"{root_path}|{json.dumps(filters_data, sort_keys=True)}|{current_depth}"
        )
        return hashlib.md5(cache_data.encode()).hexdigest()

    def _get_file_stat(self, path: str) -> tuple[bool, int]:
        """
        Кэширует результаты проверки существования файла и получения его размера.
        """
        # Check if result is already cached
        if path in self._file_stat_cache:
            return self._file_stat_cache[path]

        try:
            stat = os.stat(path)
            result = True, stat.st_size
        except OSError:
            result = False, 0

        # Cache the result
        if len(self._file_stat_cache) < 128:  # Respect the original maxsize
            self._file_stat_cache[path] = result

        return result

    def build_tree(
        self, root_path: str, filters: FilterSettings, current_depth: int = 0
    ) -> DirectoryNode | None:
        """
        Рекурсивно строит дерево файловой системы с применением фильтров.

        Args:
            root_path: Корневой путь проекта
            filters: Настройки фильтрации
            current_depth: Текущая глубина обхода (используется при рекурсии)

        Returns:
            Корневой DirectoryNode, представляющий структуру проекта, или None если корневой путь не существует
        """
        # Проверяем кэш
        cache_key = self._get_cache_key(root_path, filters, current_depth)
        if cache_key in self._cache:
            self._cache_stats["hits"] += 1
            return self._cache[cache_key]

        self._cache_stats["misses"] += 1

        # Строим дерево
        node_result: DirectoryNode | FileNode | None = self._build_node(
            root_path, filters, current_depth
        )
        # build_tree должен возвращать только DirectoryNode или None, поэтому если _build_node вернул FileNode, возвращаем None
        result: DirectoryNode | None = (
            node_result if isinstance(node_result, DirectoryNode) else None
        )
        self._cache[cache_key] = result
        return result

    def _build_node(
        self, path: str, filters: FilterSettings, current_depth: int
    ) -> DirectoryNode | FileNode | None:
        """
        Внутренний метод для построения узла дерева.

        Args:
            path: Путь к файлу или директории
            filters: Настройки фильтрации
            current_depth: Текущая глубина обхода

        Returns:
            DirectoryNode или FileNode в зависимости от типа пути
        """
        # Используем кэшированную проверку существования и размера
        exists, size = self._get_file_stat(path)
        if not exists:
            return None

        name = os.path.basename(path)

        # Проверяем, является ли путь файлом или директорией
        is_file = os.path.isfile(path)

        # Если это файл, создаем FileNode
        if is_file:
            is_binary = self._is_binary_file(path)
            file_node = FileNode(path=path, name=name, size=size, is_binary=is_binary)
            return file_node

        # Если это директория, создаем DirectoryNode
        dir_node = DirectoryNode(path=path, name=name)

        # Проверяем, должна ли директория быть исключена
        is_excluded = dir_node.is_excluded(filters)
        if is_excluded and not filters.show_excluded:
            return dir_node

        # Показываем исключенные директории, но не их содержимое
        if is_excluded and filters.show_excluded:
            return dir_node

        # Проверяем ограничение глубины из настроек фильтрации
        # Если мы достигли максимальной глубины, не сканируем содержимое директории
        if (
            filters.max_depth is not None
            and filters.max_depth >= 0
            and current_depth >= filters.max_depth
        ):
            return dir_node

        # Получаем содержимое директории
        try:
            # Используем os.scandir для более эффективного получения информации о файлах
            with os.scandir(path) as entries:
                # Сортируем записи по имени
                sorted_entries = sorted(entries, key=lambda x: x.name.lower())

                for entry in sorted_entries:
                    item_path = entry.path

                    # Рекурсивно строим дочерние узлы с увеличением глубины
                    child_node = self._build_node(item_path, filters, current_depth + 1)

                    if child_node is not None:
                        # Для файлов проверяем фильтры
                        if isinstance(child_node, FileNode):
                            if not child_node.is_excluded(filters):
                                dir_node.children.append(child_node)
                        # Для директорий добавляем только если они не исключены
                        else:
                            if not child_node.is_excluded(filters):
                                dir_node.children.append(child_node)

        except (PermissionError, OSError):
            pass

        return dir_node

    def _is_binary_file(self, file_path: str) -> bool:
        """
        Проверяет, является ли файл бинарным.

        Args:
            file_path: Путь к файлу

        Returns:
            True если файл бинарный, False в противном случае
        """
        # Check if result is already cached
        if file_path in self._is_binary_file_cache:
            return self._is_binary_file_cache[file_path]
        # Известные бинарные расширения
        binary_extensions = {
            ".pyc",
            ".pyo",
            ".exe",
            ".dll",
            ".so",
            ".dylib",
            ".bin",
            ".dat",
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".bmp",
            ".tiff",
            ".ico",
            ".mp3",
            ".mp4",
            ".avi",
            ".mkv",
            ".mov",
            ".wmv",
            ".flv",
            ".pdf",
            ".doc",
            ".docx",
            ".xls",
            ".xlsx",
            ".ppt",
            ".pptx",
            ".zip",
            ".rar",
            ".7z",
            ".tar",
            ".gz",
            ".bz2",
            ".sqlite",
            ".db",
            ".dbf",
        }

        # Проверяем расширение
        _, ext = os.path.splitext(file_path.lower())
        if ext in binary_extensions:
            return True

        # Дополнительная проверка: пытаемся прочитать первые несколько байт
        try:
            # Используем кэшированную проверку существования
            exists, size = self._get_file_stat(file_path)
            if not exists or size == 0:
                return False

            with open(file_path, "rb") as f:
                chunk = f.read(1024)
                # Если в первых 1024 байтах много нулевых байтов, это вероятно бинарный файл
                if b"\x00" in chunk:
                    return True
                # Проверяем на наличие непечатаемых символов
                try:
                    chunk.decode("utf-8")
                    return False
                except UnicodeDecodeError:
                    return True
        except OSError:
            return True

        return False
