"""Comprehensive tests for scripts/development/generate_logseq_config.py."""

from pathlib import Path
from unittest.mock import Mock, patch

from scripts.development.generate_logseq_config import generate_logseq_config


class TestGenerateLogseqConfig:
    """Test cases for generate_logseq_config function."""

    def test_generate_config_basic(self, temp_dir: Path):
        """Test basic config generation."""
        # Mock the script to use our temp directory
        with patch("scripts.development.generate_logseq_config.Path") as mock_path_class:
            # Configure mock to return our temp directory
            mock_path_instance = Mock()
            mock_path_instance.parent.parent.parent = temp_dir
            mock_path_class.return_value = mock_path_instance

            # Create some directories that should be hidden
            (temp_dir / "node_modules").mkdir()
            (temp_dir / ".git").mkdir()
            (temp_dir / ".venv").mkdir()
            (temp_dir / "tmp_cache").mkdir()
            (temp_dir / "src").mkdir()
            (temp_dir / "tests").mkdir()

            # Create knowledge base directories (should not be hidden)
            (temp_dir / "pages").mkdir()
            (temp_dir / "journals").mkdir()
            (temp_dir / "logseq").mkdir()
            (temp_dir / "assets").mkdir()

            # Mock print to avoid output
            with patch("builtins.print"):
                generate_logseq_config()

        # Check that config file was created
        config_file = temp_dir / "logseq" / "config.edn"
        assert config_file.exists()

        # Check content
        content = config_file.read_text()
        assert ":hidden" in content

        # Check that non-knowledge-base directories are hidden
        assert '"node_modules"' in content
        assert '".git"' in content
        assert '".venv"' in content
        assert '"tmp_cache"' in content
        assert '"src"' in content
        assert '"tests"' in content

        # Check that knowledge base directories are NOT hidden
        assert '"pages"' not in content
        assert '"journals"' not in content
        assert '"logseq"' not in content
        assert '"assets"' not in content

    def test_generate_config_existing_config(self, temp_dir: Path):
        """Test config generation when config already exists."""
        # Create existing config
        logseq_dir = temp_dir / "logseq"
        logseq_dir.mkdir()
        config_file = logseq_dir / "config.edn"

        existing_content = """{:meta/version 1
 :meta/config {:repos ["/path/to/repo"]}
 :feature/enable-block-timestamps? true
 :feature/enable-journals? true
 :feature/enable-flashcards? false
 :hidden ["old_dir1" "old_dir2"]
}
"""
        config_file.write_text(existing_content)

        # Mock the script to use our temp directory
        with patch("scripts.development.generate_logseq_config.Path") as mock_path_class:
            # Configure mock to return our temp directory
            mock_path_instance = Mock()
            mock_path_instance.parent.parent.parent = temp_dir
            mock_path_class.return_value = mock_path_instance

            # Create some directories
            (temp_dir / "node_modules").mkdir()
            (temp_dir / ".git").mkdir()

            # Mock print to avoid output
            with patch("builtins.print"):
                generate_logseq_config()

        # Check that config file was updated
        assert config_file.exists()
        content = config_file.read_text()

        # Check that old settings are preserved
        assert ":meta/version 1" in content
        assert ':meta/config {:repos ["/path/to/repo"]}' in content
        assert ":feature/enable-block-timestamps? true" in content

        # Check that new hidden directories are added
        assert ":hidden [" in content
        assert '"node_modules"' in content
        assert '".git"' in content

    def test_generate_config_empty_project(self, temp_dir: Path):
        """Test config generation for empty project."""
        # Mock the script to use our temp directory
        with patch("scripts.development.generate_logseq_config.Path") as mock_path_class:
            # Configure mock to return our temp directory
            mock_path_instance = Mock()
            mock_path_instance.parent.parent.parent = temp_dir
            mock_path_class.return_value = mock_path_instance

            # Create only knowledge base directories
            (temp_dir / "pages").mkdir()
            (temp_dir / "journals").mkdir()
            (temp_dir / "logseq").mkdir()
            (temp_dir / "assets").mkdir()

            # Mock print to avoid output
            with patch("builtins.print"):
                generate_logseq_config()

        # Check that config file was created
        config_file = temp_dir / "logseq" / "config.edn"
        assert config_file.exists()

        # Check content
        content = config_file.read_text()
        assert ":hidden []" in content  # Empty hidden list

        # Check comment
        assert "Этот блок сгенерирован автоматически" in content

    def test_generate_config_complex_structure(self, temp_dir: Path):
        """Test config generation with complex directory structure."""
        # Mock the script to use our temp directory
        with patch("scripts.development.generate_logseq_config.Path") as mock_path_class:
            # Configure mock to return our temp directory
            mock_path_instance = Mock()
            mock_path_instance.parent.parent.parent = temp_dir
            mock_path_class.return_value = mock_path_instance

            # Create complex structure
            (temp_dir / "node_modules" / "package1").mkdir(parents=True)
            (temp_dir / ".git" / "objects").mkdir(parents=True)
            (temp_dir / ".venv" / "lib" / "python3.9").mkdir(parents=True)
            (temp_dir / "tmp_cache" / "pytest").mkdir(parents=True)
            (temp_dir / "build" / "dist").mkdir(parents=True)
            (temp_dir / "dist").mkdir()
            (temp_dir / "__pycache__").mkdir()
            (temp_dir / ".pytest_cache").mkdir()
            (temp_dir / ".mypy_cache").mkdir()

            # Create knowledge base directories
            (temp_dir / "pages").mkdir()
            (temp_dir / "journals").mkdir()
            (temp_dir / "logseq").mkdir()
            (temp_dir / "assets").mkdir()

            # Mock print to avoid output
            with patch("builtins.print"):
                generate_logseq_config()

        # Check that config file was created
        config_file = temp_dir / "logseq" / "config.edn"
        assert config_file.exists()

        # Check content
        content = config_file.read_text()
        assert ":hidden [" in content

        # Check that all non-knowledge-base directories are hidden
        hidden_dirs = [
            "node_modules",
            ".git",
            ".venv",
            "tmp_cache",
            "build",
            "dist",
            "__pycache__",
            ".pytest_cache",
            ".mypy_cache",
        ]

        for dir_name in hidden_dirs:
            assert f'"{dir_name}"' in content

        # Check that knowledge base directories are NOT hidden
        kb_dirs = ["pages", "journals", "logseq", "assets"]
        for dir_name in kb_dirs:
            assert f'"{dir_name}"' not in content

    def test_generate_config_output_format(self, temp_dir: Path):
        """Test that generated config has correct format."""
        # Mock the script to use our temp directory
        with patch("scripts.development.generate_logseq_config.Path") as mock_path_class:
            # Configure mock to return our temp directory
            mock_path_instance = Mock()
            mock_path_instance.parent.parent.parent = temp_dir
            mock_path_class.return_value = mock_path_instance

            # Create some directories
            (temp_dir / "node_modules").mkdir()
            (temp_dir / ".git").mkdir()

            # Mock print to capture output
            with patch("builtins.print") as mock_print:
                generate_logseq_config()

        # Check that output was printed
        mock_print.assert_called()
        printed_output = " ".join(str(call) for call in mock_print.call_args_list)

        # Check success message
        assert "успешно обновлен" in printed_output
        assert "logseq/config.edn" in printed_output

        # Check config content display
        assert "Содержимое config.edn:" in printed_output

        # Check config file
        config_file = temp_dir / "logseq" / "config.edn"
        content = config_file.read_text()

        # Check format
        assert content.startswith(" ;;") or content.startswith("{")
        assert ":hidden [" in content
        assert "]" in content

    def test_generate_config_logseq_dir_creation(self, temp_dir: Path):
        """Test that logseq directory is created if it doesn't exist."""
        # Mock the script to use our temp directory
        with patch("scripts.development.generate_logseq_config.Path") as mock_path_class:
            # Configure mock to return our temp directory
            mock_path_instance = Mock()
            mock_path_instance.parent.parent.parent = temp_dir
            mock_path_class.return_value = mock_path_instance

            # Don't create logseq directory initially
            (temp_dir / "pages").mkdir()
            (temp_dir / "journals").mkdir()
            (temp_dir / "assets").mkdir()

            # Mock print to avoid output
            with patch("builtins.print"):
                generate_logseq_config()

        # Check that logseq directory was created
        logseq_dir = temp_dir / "logseq"
        assert logseq_dir.exists()
        assert logseq_dir.is_dir()

        # Check that config file was created
        config_file = logseq_dir / "config.edn"
        assert config_file.exists()

    def test_generate_config_no_duplicate_entries(self, temp_dir: Path):
        """Test that no duplicate entries are created in hidden list."""
        # Create existing config with some overlaps
        logseq_dir = temp_dir / "logseq"
        logseq_dir.mkdir()
        config_file = logseq_dir / "config.edn"

        existing_content = """{:hidden [".git" "node_modules"]}
"""
        config_file.write_text(existing_content)

        # Mock the script to use our temp directory
        with patch("scripts.development.generate_logseq_config.Path") as mock_path_class:
            # Configure mock to return our temp directory
            mock_path_instance = Mock()
            mock_path_instance.parent.parent.parent = temp_dir
            mock_path_class.return_value = mock_path_instance

            # Create directories (including some that might be duplicates)
            (temp_dir / "node_modules").mkdir()
            (temp_dir / ".git").mkdir()
            (temp_dir / ".venv").mkdir()

            # Mock print to avoid output
            with patch("builtins.print"):
                generate_logseq_config()

        # Check final content
        content = config_file.read_text()

        # Count occurrences of each directory
        git_count = content.count('".git"')
        node_modules_count = content.count('"node_modules"')
        venv_count = content.count('".venv"')

        # Should have exactly one occurrence of each
        assert git_count == 1
        assert node_modules_count == 1
        assert venv_count == 1


class TestIntegration:
    """Integration tests for the config generator."""

    def test_complete_workflow(self, temp_dir: Path):
        """Test complete workflow with realistic project structure."""
        # Create realistic project structure
        dirs_to_create = [
            "pages",
            "journals",
            "logseq",
            "assets",  # Knowledge base
            "src/code2markdown",
            "tests",
            "scripts/development",  # Project dirs
            "node_modules/package",
            ".git/objects",
            ".venv/lib",  # Hidden dirs
            "build/dist",
            "tmp_cache",
            "__pycache__",
            ".pytest_cache",  # Hidden dirs
        ]

        for dir_path in dirs_to_create:
            (temp_dir / dir_path).mkdir(parents=True)

        # Create some files
        (temp_dir / "pages" / "STORY-API-1.md").write_text("# User Story")
        (temp_dir / "src" / "main.py").write_text("# Main module")

        # Mock the script to use our temp directory
        with patch("scripts.development.generate_logseq_config.Path") as mock_path_class:
            # Configure mock to return our temp directory
            mock_path_instance = Mock()
            mock_path_instance.parent.parent.parent = temp_dir
            mock_path_class.return_value = mock_path_instance

            # Mock print to capture output
            with patch("builtins.print") as mock_print:
                generate_logseq_config()

        # Check that config file was created
        config_file = temp_dir / "logseq" / "config.edn"
        assert config_file.exists()

        # Check content
        content = config_file.read_text()

        # Verify hidden directories
        hidden_dirs = [
            "src",
            "tests",
            "scripts",
            "node_modules",
            ".git",
            ".venv",
            "build",
            "tmp_cache",
            "__pycache__",
            ".pytest_cache",
        ]

        for dir_name in hidden_dirs:
            assert f'"{dir_name}"' in content

        # Verify knowledge base directories are NOT hidden
        kb_dirs = ["pages", "journals", "logseq", "assets"]
        for dir_name in kb_dirs:
            assert f'"{dir_name}"' not in content

        # Check output was printed
        mock_print.assert_called()
        printed_output = " ".join(str(call) for call in mock_print.call_args_list)
        assert "успешно обновлен" in printed_output

    def test_config_preserves_other_settings(self, temp_dir: Path):
        """Test that existing config settings are preserved."""
        # Create existing config with various settings
        logseq_dir = temp_dir / "logseq"
        logseq_dir.mkdir()
        config_file = logseq_dir / "config.edn"

        existing_content = """{:meta/version 2
 :meta/config {:repos ["/path/to/repo" "/another/repo"]}
 :feature/enable-block-timestamps? true
 :feature/enable-journals? true
 :feature/enable-flashcards? false
 :feature/enable-whiteboards? true
 :feature/enable-sync? false
 :ui/theme "dark"
 :ui/font-size 14
 :editor/extra-codemirror-options {:keyMap "vim"}
 :hidden ["old_dir1" "old_dir2"]
}
"""
        config_file.write_text(existing_content)

        # Mock the script to use our temp directory
        with patch("scripts.development.generate_logseq_config.Path") as mock_path_class:
            # Configure mock to return our temp directory
            mock_path_instance = Mock()
            mock_path_instance.parent.parent.parent = temp_dir
            mock_path_class.return_value = mock_path_instance

            # Create some directories
            (temp_dir / "node_modules").mkdir()

            # Mock print to avoid output
            with patch("builtins.print"):
                generate_logseq_config()

        # Check that all original settings are preserved
        content = config_file.read_text()

        # Check meta settings
        assert ":meta/version 2" in content
        assert ':repos ["/path/to/repo" "/another/repo"]' in content

        # Check feature settings
        assert ":feature/enable-block-timestamps? true" in content
        assert ":feature/enable-journals? true" in content
        assert ":feature/enable-flashcards? false" in content
        assert ":feature/enable-whiteboards? true" in content
        assert ":feature/enable-sync? false" in content

        # Check UI settings
        assert ':ui/theme "dark"' in content
        assert ":ui/font-size 14" in content

        # Check editor settings
        assert ':editor/extra-codemirror-options {:keyMap "vim"}' in content

        # Check new hidden directories are added
        assert '"node_modules"' in content

    def test_performance_with_many_directories(self, temp_dir: Path):
        """Test performance with many directories."""
        # Create many directories
        for i in range(50):
            (temp_dir / f"dir_{i}").mkdir()

        # Add knowledge base directories
        (temp_dir / "pages").mkdir()
        (temp_dir / "journals").mkdir()
        (temp_dir / "logseq").mkdir()
        (temp_dir / "assets").mkdir()

        # Mock the script to use our temp directory
        with patch("scripts.development.generate_logseq_config.Path") as mock_path_class:
            # Configure mock to return our temp directory
            mock_path_instance = Mock()
            mock_path_instance.parent.parent.parent = temp_dir
            mock_path_class.return_value = mock_path_instance

            # Mock print to avoid output
            with patch("builtins.print"):
                # Measure execution time
                import time

                start_time = time.time()
                generate_logseq_config()
                end_time = time.time()
                execution_time = end_time - start_time

        # Should complete quickly (< 1 second for 54 directories)
        assert execution_time < 1.0

        # Check config file
        config_file = temp_dir / "logseq" / "config.edn"
        assert config_file.exists()

        # Check that many directories are hidden
        content = config_file.read_text()
        hidden_count = content.count('"')

        # Should have around 50 hidden directories (2 quotes each)
        assert hidden_count >= 90  # At least 45 directories (90 quotes)

        # Knowledge base directories should not be hidden
        assert '"pages"' not in content
        assert '"journals"' not in content
        assert '"logseq"' not in content
        assert '"assets"' not in content
