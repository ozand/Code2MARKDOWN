#!/usr/bin/env python3
"""
Простой тест для проверки работы GenerationService
"""

import os
import tempfile
from unittest.mock import Mock

from code2markdown.application.services import GenerationService
from code2markdown.application.repository import IHistoryRepository
from code2markdown.domain.filters import FileSize, FilterSettings

def test_generation_service():
    """Тестируем работу GenerationService"""
    print("🔍 Тестирование работы GenerationService")
    print("=" * 50)
    
    # Создаем временную директорию с тестовыми файлами
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"📁 Временная директория: {temp_dir}")
        
        # Создаем тестовые файлы
        with open(os.path.join(temp_dir, "main.py"), "w") as f:
            f.write("# Main Python file\nprint('Hello')")
            
        with open(os.path.join(temp_dir, "README.md"), "w") as f:
            f.write("# Project Documentation\nThis is a test.")
        
        # Настройки фильтров
        filters = FilterSettings(
            include_patterns=[".py", ".md"],
            exclude_patterns=["__pycache__", ".git"],
            max_file_size=FileSize(kb=100),
            show_excluded=False,
        )
        
        print(f"📥 Include patterns: {filters.include_patterns}")
        print(f"📤 Exclude patterns: {filters.exclude_patterns}")
        print(f"📊 Max file size: {filters.max_file_size.kb} KB")
        print()
        
        # Создаем мок репозитория
        mock_repo = Mock(spec=IHistoryRepository)
        
        # Создаем сервис
        service = GenerationService(history_repo=mock_repo)
        
        # Создаем простой шаблон
        template_content = "# Project: {{ absolute_code_path }}\n\n{{ source_tree }}\n\n{{#each files}}\n{{path}}:\n```\n{{code}}\n```\n{{/each}}"
        
        # Мокаем загрузку шаблона
        from unittest.mock import patch
        with patch.object(service, '_load_template') as mock_load_template:
            # Настраиваем мок
            mock_template = Mock()
            mock_template.return_value = "# Generated Documentation\nContent here"
            mock_load_template.return_value = mock_template
            
            # Пытаемся сгенерировать документацию
            try:
                result = service.generate_and_save_documentation(
                    project_path=temp_dir,
                    template_name="test_template.hbs",
                    filters=filters,
                )
                
                print("✅ Генерация документации прошла успешно")
                print(f"📝 Результат: {result[:100]}...")
                
                # Проверяем, что репозиторий был вызван
                if mock_repo.save.called:
                    print("💾 Репозиторий был вызван для сохранения")
                    saved_request = mock_repo.save.call_args[0][0]
                    print(f"📊 Количество файлов: {saved_request.file_count}")
                    print(f"📁 Путь к проекту: {saved_request.project_path}")
                else:
                    print("❌ Репозиторий не был вызван")
                    
            except Exception as e:
                print(f"❌ Ошибка при генерации: {e}")
                import traceback
                traceback.print_exc()

if __name__ == "__main__":
    test_generation_service()