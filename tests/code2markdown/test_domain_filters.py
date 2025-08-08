import pytest

from code2markdown.domain.filters import FileSize, FilterSettings


class TestFileSize:
    def test_positive_size(self):
        """Тест валидных значений для FileSize"""
        # Проверяем создание с положительными значениями
        size = FileSize(kb=1)
        assert size.kb == 1
        assert size.bytes == 1024

        size = FileSize(kb=100)
        assert size.kb == 100
        assert size.bytes == 102400

    def test_non_positive_size(self):
        """Тест невалидных значений для FileSize (ожидается исключение)"""
        # Проверяем создание с нулевым значением
        with pytest.raises(
            ValueError, match="Размер файла должен быть положительным числом."
        ):
            FileSize(kb=0)

        # Проверяем создание с отрицательным значением
        with pytest.raises(
            ValueError, match="Размер файла должен быть положительным числом."
        ):
            FileSize(kb=-1)

        # Проверяем создание с отрицательным значением
        with pytest.raises(
            ValueError, match="Размер файла должен быть положительным числом."
        ):
            FileSize(kb=-10)


class TestFilterSettings:
    def test_valid_settings(self):
        """Тест валидных настроек для FilterSettings"""
        # Проверяем создание с валидными параметрами
        settings = FilterSettings(
            include_patterns=[".py", ".txt"],
            exclude_patterns=["node_modules", ".git"],
            max_file_size=FileSize(kb=50),
            show_excluded=True,
        )

        assert settings.include_patterns == [".py", ".txt"]
        assert settings.exclude_patterns == ["node_modules", ".git"]
        assert settings.max_file_size.kb == 50
        assert settings.show_excluded is True

        # Проверяем с пустыми списками
        settings = FilterSettings(
            include_patterns=[], exclude_patterns=[], max_file_size=FileSize(kb=100)
        )

        assert settings.include_patterns == []
        assert settings.exclude_patterns == []
        assert settings.max_file_size.kb == 100
        assert settings.show_excluded is False  # значение по умолчанию

    def test_invalid_patterns_type(self):
        """Тест невалидных типов для паттернов (ожидается исключение)"""
        # Проверяем с несписковым include_patterns
        with pytest.raises(
            ValueError, match="include_patterns должен быть списком строк"
        ):
            FilterSettings(include_patterns="not_a_list")

        # Проверяем с несписковым exclude_patterns
        with pytest.raises(
            ValueError, match="exclude_patterns должен быть списком строк"
        ):
            FilterSettings(exclude_patterns="not_a_list")

        # Проверяем с несписковыми обоими паттернами
        with pytest.raises(
            ValueError, match="include_patterns должен быть списком строк"
        ):
            FilterSettings(include_patterns="not_a_list", exclude_patterns="not_a_list")

        # Проверяем с None
        with pytest.raises(
            ValueError, match="include_patterns должен быть списком строк"
        ):
            FilterSettings(include_patterns=None)

        # Проверяем с числом
        with pytest.raises(
            ValueError, match="include_patterns должен быть списком строк"
        ):
            FilterSettings(include_patterns=123)

        # Проверяем со словарем
        with pytest.raises(
            ValueError, match="include_patterns должен быть списком строк"
        ):
            FilterSettings(include_patterns={"key": "value"})

    def test_invalid_patterns_elements(self):
        """Тест невалидных элементов внутри списков паттернов"""
        # Проверяем с нестроковыми элементами в include_patterns
        with pytest.raises(
            ValueError, match="Все элементы include_patterns должны быть строками"
        ):
            FilterSettings(include_patterns=[".py", 123])

        # Проверяем с нестроковыми элементами в exclude_patterns
        with pytest.raises(
            ValueError, match="Все элементы exclude_patterns должны быть строками"
        ):
            FilterSettings(exclude_patterns=["node_modules", None])

        # Проверяем с нестроковыми элементами в обоих списках
        with pytest.raises(
            ValueError, match="Все элементы include_patterns должны быть строками"
        ):
            FilterSettings(
                include_patterns=[".py", 123], exclude_patterns=["node_modules", 456]
            )
