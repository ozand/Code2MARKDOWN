"""Critical E2E test flows for Code2Markdown application."""

import pytest
from pathlib import Path
from playwright.sync_api import Page, expect
from tests.e2e.pages.main_page import MainPage
from tests.e2e.data import TestDataManager, PythonFileFactory, TEST_DATA_TEMPLATES


class TestCriticalFlows:
    """Test critical user flows for the Code2Markdown application."""
    
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Set up test environment."""
        self.page = page
        self.main_page = MainPage(page)
        self.test_data_manager = TestDataManager()
        self.factory = PythonFileFactory()
    
    def teardown_method(self):
        """Clean up test data after each test."""
        self.test_data_manager.cleanup_all()
    
    def test_basic_file_conversion_flow(self):
        """Test basic file conversion from upload to markdown generation."""
        # Arrange
        test_file = self.test_data_manager.create_test_file(
            "simple_test.py",
            TEST_DATA_TEMPLATES["simple_function"]
        )
        
        # Act - Navigate to main page
        self.main_page.navigate()
        
        # Verify page loaded correctly
        expect(self.main_page.page).to_have_title(self.main_page.title)
        
        # Upload file
        self.main_page.upload_file(test_file)
        
        # Wait for file to be processed
        self.main_page.wait_for_generation_complete()
        
        # Generate markdown
        markdown_content = self.main_page.get_markdown_output()
        
        # Assert
        assert markdown_content is not None
        assert "def greet" in markdown_content
        assert "Hello" in markdown_content
        assert "name: str" in markdown_content
        assert "-> str" in markdown_content
    
    def test_multiple_file_upload_and_conversion(self):
        """Test uploading and converting multiple Python files."""
        # Arrange
        test_files = self.test_data_manager.create_multiple_test_files(3, "multi_test")
        
        # Act
        self.main_page.navigate()
        
        # Upload multiple files
        for test_file in test_files:
            self.main_page.upload_file(test_file)
        
        # Wait for processing
        self.main_page.wait_for_generation_complete()
        
        # Generate markdown
        markdown_content = self.main_page.get_markdown_output()
        
        # Assert
        assert markdown_content is not None
        # Should contain content from multiple files
        assert len(markdown_content) > 1000  # Reasonable minimum length
    
    def test_class_documentation_generation(self):
        """Test documentation generation for Python classes."""
        # Arrange
        test_file = self.test_data_manager.create_test_file(
            "test_class.py",
            TEST_DATA_TEMPLATES["simple_class"]
        )
        
        # Act
        self.main_page.navigate()
        self.main_page.upload_file(test_file)
        self.main_page.wait_for_generation_complete()
        markdown_content = self.main_page.get_markdown_output()
        
        # Assert
        assert "class Calculator" in markdown_content
        assert "add" in markdown_content
        assert "multiply" in markdown_content
        assert "Simple calculator class" in markdown_content
    
    def test_complex_module_documentation(self):
        """Test documentation generation for complex Python modules."""
        # Arrange
        test_file = self.test_data_manager.create_test_file(
            "complex_module.py",
            TEST_DATA_TEMPLATES["complex_module"]
        )
        
        # Act
        self.main_page.navigate()
        self.main_page.upload_file(test_file)
        self.main_page.wait_for_generation_complete()
        markdown_content = self.main_page.get_markdown_output()
        
        # Assert
        assert "Advanced data processing module" in markdown_content
        assert "DataPoint" in markdown_content
        assert "DataProcessor" in markdown_content
        assert "process_data" in markdown_content
        assert "export_results" in markdown_content
    
    def test_error_handling_for_invalid_file(self):
        """Test error handling when uploading invalid Python files."""
        # Arrange
        invalid_file = self.test_data_manager.create_test_file(
            "invalid.py",
            self.factory.create_invalid_python_file()
        )
        
        # Act
        self.main_page.navigate()
        self.main_page.upload_file(invalid_file)
        
        # Wait and check for error handling
        # The application should handle this gracefully
        self.main_page.wait_for_generation_complete(timeout=10000)
        
        # Assert - should not crash, might show error message
        # The exact behavior depends on the application's error handling
        current_url = self.page.url
        assert "error" not in current_url.lower()  # Should not redirect to error page
    
    def test_file_selection_and_filtering(self):
        """Test file selection and filtering functionality."""
        # Arrange
        test_files = [
            self.test_data_manager.create_test_file("test1.py", "print('hello')"),
            self.test_data_manager.create_test_file("test2.txt", "not python code"),
            self.test_data_manager.create_test_file("test3.py", "def func(): pass"),
        ]
        
        # Act
        self.main_page.navigate()
        
        # Upload mixed file types
        for test_file in test_files:
            self.main_page.upload_file(test_file)
        
        self.main_page.wait_for_generation_complete()
        
        # Should only process Python files
        markdown_content = self.main_page.get_markdown_output()
        
        # Assert
        assert markdown_content is not None
        # Should contain Python code but not text file content
        assert "print('hello')" in markdown_content or "def func" in markdown_content
        assert "not python code" not in markdown_content
    
    def test_navigation_and_ui_elements(self):
        """Test navigation and basic UI elements are present."""
        # Act
        self.main_page.navigate()
        
        # Assert
        # Check for main UI elements
        expect(self.main_page.page.locator("h1")).to_be_visible()
        expect(self.main_page.page.locator("input[type='file']")).to_be_visible()
        
        # Check page title and URL
        expect(self.main_page.page).to_have_title(self.main_page.title)
        expect(self.main_page.page).to_have_url(f"{self.main_page.base_url}{self.main_page.path}")
    
    def test_responsive_design_elements(self):
        """Test that UI elements are responsive and accessible."""
        # Act
        self.main_page.navigate()
        
        # Test different viewport sizes
        viewport_sizes = [
            {"width": 1920, "height": 1080},  # Desktop
            {"width": 768, "height": 1024},   # Tablet
            {"width": 375, "height": 667},    # Mobile
        ]
        
        for viewport in viewport_sizes:
            self.page.set_viewport_size(viewport)
            
            # Assert elements are still visible and functional
            expect(self.main_page.page.locator("h1")).to_be_visible()
            expect(self.main_page.page.locator("input[type='file']")).to_be_visible()
    
    def test_download_functionality(self):
        """Test markdown download functionality."""
        # Arrange
        test_file = self.test_data_manager.create_test_file(
            "download_test.py",
            TEST_DATA_TEMPLATES["simple_function"]
        )
        
        # Act
        self.main_page.navigate()
        self.main_page.upload_file(test_file)
        self.main_page.wait_for_generation_complete()
        
        # Download the generated markdown
        download_path = self.main_page.download_markdown()
        
        # Assert
        assert download_path is not None
        assert download_path.exists()
        
        # Verify downloaded content
        downloaded_content = download_path.read_text(encoding='utf-8')
        assert "def greet" in downloaded_content
        assert len(downloaded_content) > 0
    
    def test_clear_functionality(self):
        """Test clear/reset functionality."""
        # Arrange
        test_file = self.test_data_manager.create_test_file(
            "clear_test.py",
            TEST_DATA_TEMPLATES["simple_function"]
        )
        
        # Act
        self.main_page.navigate()
        self.main_page.upload_file(test_file)
        self.main_page.wait_for_generation_complete()
        
        # Clear the content
        self.main_page.clear_content()
        
        # Assert - should reset to initial state
        # Implementation depends on how clear functionality works in the app
        expect(self.main_page.page.locator("input[type='file']")).to_be_visible()
    
    @pytest.mark.parametrize("template_name", ["simple_function", "simple_class", "complex_module"])
    def test_template_variations(self, template_name):
        """Test documentation generation with different template types."""
        # Arrange
        template_content = TEST_DATA_TEMPLATES[template_name]
        test_file = self.test_data_manager.create_test_file(
            f"{template_name}_test.py",
            template_content
        )
        
        # Act
        self.main_page.navigate()
        self.main_page.upload_file(test_file)
        self.main_page.wait_for_generation_complete()
        markdown_content = self.main_page.get_markdown_output()
        
        # Assert
        assert markdown_content is not None
        assert len(markdown_content) > 100  # Minimum reasonable length
        
        # Template-specific assertions
        if template_name == "simple_function":
            assert "def greet" in markdown_content
        elif template_name == "simple_class":
            assert "class Calculator" in markdown_content
        elif template_name == "complex_module":
            assert "Advanced data processing module" in markdown_content
    
    def test_empty_file_handling(self):
        """Test handling of empty Python files."""
        # Arrange
        empty_file = self.test_data_manager.create_test_file("empty.py", "")
        
        # Act
        self.main_page.navigate()
        self.main_page.upload_file(empty_file)
        self.main_page.wait_for_generation_complete()
        
        # Should handle gracefully without errors
        current_url = self.page.url
        assert "error" not in current_url.lower()
    
    def test_large_file_handling(self):
        """Test handling of large Python files."""
        # Arrange - create a large file with many functions
        large_content = ""
        for i in range(100):
            large_content += f"def function_{i}():\n    return {i}\n\n"
        
        large_file = self.test_data_manager.create_test_file("large_file.py", large_content)
        
        # Act
        self.main_page.navigate()
        self.main_page.upload_file(large_file)
        self.main_page.wait_for_generation_complete(timeout=30000)  # Longer timeout for large files
        
        markdown_content = self.main_page.get_markdown_output()
        
        # Assert
        assert markdown_content is not None
        assert "function_0" in markdown_content
        assert "function_99" in markdown_content
    
    def test_concurrent_file_processing(self):
        """Test processing multiple files concurrently."""
        # Arrange
        test_files = []
        for i in range(5):
            content = f"def func_{i}():\\n    return {i}"
            test_file = self.test_data_manager.create_test_file(f"concurrent_{i}.py", content)
            test_files.append(test_file)
        
        # Act
        self.main_page.navigate()
        
        # Upload all files quickly
        for test_file in test_files:
            self.main_page.upload_file(test_file)
        
        self.main_page.wait_for_generation_complete()
        markdown_content = self.main_page.get_markdown_output()
        
        # Assert
        assert markdown_content is not None
        # Should contain functions from all files
        for i in range(5):
            assert f"func_{i}" in markdown_content