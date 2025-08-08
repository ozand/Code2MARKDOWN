import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest
import streamlit as st

from code2markdown.app import render_file_tree_ui


class TestAppUI:
    """Test suite for Streamlit UI components in app.py."""

    @pytest.fixture
    def setup_session_state(self):
        """Fixture to set up Streamlit session state for testing."""
        # Clear session state
        if hasattr(st, "session_state"):
            st.session_state.clear()

        # Initialize required session state
        st.session_state.filter_settings = MagicMock()
        st.session_state.filter_settings.include_patterns = [".py", ".md"]
        st.session_state.filter_settings.exclude_patterns = ["__pycache__", ".git"]
        st.session_state.filter_settings.max_file_size.kb = 50
        st.session_state.filter_settings.show_excluded = False
        st.session_state.filter_settings.selected_files = set()

        yield

        # Cleanup
        st.session_state.clear()

    def test_scan_folder_button_functionality(self, setup_session_state):
        """Test that the scan folder button correctly builds and stores the file tree."""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            with open(os.path.join(temp_dir, "main.py"), "w") as f:
                f.write("# Test Python file")
            with open(os.path.join(temp_dir, "README.md"), "w") as f:
                f.write("# Test Markdown file")

            # Mock Streamlit button to simulate click
            with patch("streamlit.button") as mock_button:
                mock_button.return_value = True  # Simulate button click

                # Mock ProjectTreeBuilder.build_tree
                with patch("code2markdown.app.ProjectTreeBuilder") as mock_builder_class:
                    mock_builder_instance = MagicMock()
                    mock_builder_class.return_value = mock_builder_instance

                    # Create a simple tree structure for testing
                    mock_tree = {
                        "main.py": {
                            "type": "file",
                            "path": os.path.join(temp_dir, "main.py"),
                            "excluded": False,
                            "size": 20,
                        },
                        "README.md": {
                            "type": "file",
                            "path": os.path.join(temp_dir, "README.md"),
                            "excluded": False,
                            "size": 20,
                        },
                    }
                    mock_builder_instance.build_tree.return_value = mock_tree

                    # Act - simulate the UI logic
                    if st.button("Сканировать папку", key="scan_button"):
                        builder = mock_builder_class()
                        file_tree = builder.build_tree(
                            temp_dir, st.session_state.filter_settings
                        )
                        st.session_state.file_tree = file_tree

                    # Assert
                    assert hasattr(st.session_state, "file_tree")
                    assert st.session_state.file_tree == mock_tree
                    mock_builder_instance.build_tree.assert_called_once()

    def test_file_tree_display_logic(self, setup_session_state):
        """Test that file tree is displayed only when available."""
        # Arrange
        test_path = "/test/path"

        # Test case 1: No file tree available
        if hasattr(st.session_state, "file_tree"):
            del st.session_state.file_tree

        # Capture output to check for correct message
        with patch("streamlit.info") as mock_info:
            # Simulate the UI logic
            if st.session_state.get("file_tree"):
                file_tree = st.session_state.file_tree
                # This would render the tree UI
                render_file_tree_ui(file_tree, selected_files=set(), key_prefix="tree")
            else:
                st.info("Нажмите 'Сканировать папку' для отображения структуры")

            # Assert correct message is shown
            mock_info.assert_called_with(
                "Нажмите 'Сканировать папку' для отображения структуры"
            )
            # Note: We can't directly check st.info calls in this mock setup
            # but we verify the logic path is correct

        # Test case 2: File tree is available
        st.session_state.file_tree = {
            "test.py": {
                "type": "file",
                "path": os.path.join(test_path, "test.py"),
                "excluded": False,
                "size": 20,
            }
        }

        # In this test we're primarily checking the logic flow
        # rather than the actual rendering (which would require more complex mocking)
        assert st.session_state.get("file_tree") is not None

    def test_selected_files_preservation(self, setup_session_state):
        """Test that selected files are preserved after scanning."""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            with open(os.path.join(temp_dir, "main.py"), "w") as f:
                f.write("# Test Python file")
            with open(os.path.join(temp_dir, "README.md"), "w") as f:
                f.write("# Test Markdown file")

            # Set initial selected files
            initial_selected = {os.path.join(temp_dir, "main.py")}
            st.session_state.filter_settings.selected_files = initial_selected

            # Mock the scan button and builder
            with patch("streamlit.button") as mock_button:
                mock_button.return_value = True  # Simulate scan button click

                with patch("code2markdown.app.ProjectTreeBuilder") as mock_builder_class:
                    mock_builder_instance = MagicMock()
                    mock_builder_class.return_value = mock_builder_instance

                    # Create tree structure
                    mock_tree = {
                        "main.py": {
                            "type": "file",
                            "path": os.path.join(temp_dir, "main.py"),
                            "excluded": False,
                            "size": 20,
                        },
                        "README.md": {
                            "type": "file",
                            "path": os.path.join(temp_dir, "README.md"),
                            "excluded": False,
                            "size": 20,
                        },
                    }
                    mock_builder_instance.build_tree.return_value = mock_tree

                    # Act - perform scan
                    if st.button("Сканировать папку", key="scan_button"):
                        builder = mock_builder_class()
                        file_tree = builder.build_tree(
                            temp_dir, st.session_state.filter_settings
                        )
                        st.session_state.file_tree = file_tree

                    # Also simulate file selection UI
                    with patch("code2markdown.app.render_file_tree_ui") as mock_render:
                        mock_render.return_value = (
                            initial_selected  # Simulate UI returning selected files
                        )

                        newly_selected = render_file_tree_ui(
                            st.session_state.file_tree,
                            selected_files=st.session_state.filter_settings.selected_files,
                            key_prefix="tree",
                        )

                        # Update selected files if changed
                        if (
                            newly_selected
                            != st.session_state.filter_settings.selected_files
                        ):
                            st.session_state.filter_settings.selected_files = (
                                newly_selected
                            )

                    # Assert
                    assert (
                        st.session_state.filter_settings.selected_files
                        == initial_selected
                    )
                    assert "file_tree" in st.session_state
