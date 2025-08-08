from dataclasses import dataclass, field


@dataclass
class FileSize:
    """Value Object для размера файла в килобайтах."""

    kb: int

    def __post_init__(self):
        if self.kb <= 0:
            raise ValueError("Размер файла должен быть положительным числом.")

    @property
    def bytes(self) -> int:
        return self.kb * 1024


@dataclass
class FilterSettings:
    """Value Object, инкапсулирующий все настройки фильтрации."""

    include_patterns: list[str] = field(default_factory=list)
    exclude_patterns: list[str] = field(default_factory=list)
    max_file_size: FileSize = field(default_factory=lambda: FileSize(kb=50))
    show_excluded: bool = False
    selected_files: set[str] | None = field(default_factory=set)
    max_depth: int | None = None  # None - без ограничений, иначе максимальная глубина

    def __post_init__(self):
        """Проверяет, что include_patterns и exclude_patterns являются списками строк."""
        if not isinstance(self.include_patterns, list):
            raise ValueError("include_patterns должен быть списком строк")
        if not isinstance(self.exclude_patterns, list):
            raise ValueError("exclude_patterns должен быть списком строк")
        # Проверяем, что все элементы в списках являются строками
        for pattern in self.include_patterns:
            if not isinstance(pattern, str):
                raise ValueError("Все элементы include_patterns должны быть строками")
        for pattern in self.exclude_patterns:
            if not isinstance(pattern, str):
                raise ValueError("Все элементы exclude_patterns должны быть строками")
