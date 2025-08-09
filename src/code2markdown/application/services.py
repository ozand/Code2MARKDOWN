import html
import os
from datetime import datetime

from pybars import Compiler

from code2markdown.application.repository import IHistoryRepository
from code2markdown.domain.files import DirectoryNode, FileNode, ProjectTreeBuilder
from code2markdown.domain.filters import FilterSettings
from code2markdown.domain.request import GenerationRequest


class GenerationService:
    """
    Service class responsible for generating documentation and saving it to the history repository.
    """

    def __init__(
        self, history_repo: IHistoryRepository, templates_dir: str | None = None
    ):
        """
        Initialize the GenerationService with a history repository.

        Args:
            history_repo: An instance of IHistoryRepository for saving generation requests
            templates_dir: Path to the directory with templates. If None, default paths are used.
        """
        self._history_repo = history_repo
        self._templates_dir = templates_dir

    def _load_template(self, template_name: str) -> Compiler | None:
        """
        Load a Handlebars template from the templates directory.

        Args:
            template_name: Name of the template file

        Returns:
            Compiled template or None if template not found
        """
        # If templates_dir is specified, use it
        if self._templates_dir:
            template_path = os.path.join(self._templates_dir, template_name)
            if os.path.exists(template_path):
                with open(template_path, encoding="utf-8") as template_file:
                    return Compiler().compile(template_file.read())
            return None

        # First try in project's templates directory
        project_template_path = os.path.join(os.getcwd(), "templates", template_name)
        if os.path.exists(project_template_path):
            with open(project_template_path, encoding="utf-8") as template_file:
                return Compiler().compile(template_file.read())

        # Then try in application's templates directory
        app_template_path = os.path.join("templates", template_name)
        if os.path.exists(app_template_path):
            with open(app_template_path, encoding="utf-8") as template_file:
                return Compiler().compile(template_file.read())

        return None

    def _is_binary_file(self, file_path: str) -> bool:
        """
        Check if a file is binary by examining its extension and content.

        Args:
            file_path: Path to the file to check

        Returns:
            True if the file is binary, False otherwise
        """
        # Known binary extensions
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

        # Check extension
        _, ext = os.path.splitext(file_path.lower())
        if ext in binary_extensions:
            return True

        # Additional check: try to read first few bytes
        try:
            with open(file_path, "rb") as f:
                chunk = f.read(1024)
                # If there are many null bytes, it's likely binary
                if b"\x00" in chunk:
                    return True
                # Check for non-printable characters
                try:
                    chunk.decode("utf-8")
                    return False
                except UnicodeDecodeError:
                    return True
        except OSError:
            return True

        return False

    def _build_project_structure_from_tree(
        self, node: DirectoryNode, selected_files: list[str] | None = None
    ) -> str:
        """
        Build project structure string from DirectoryNode tree.

        Args:
            node: Root node of the directory tree
            selected_files: Optional list of selected files to filter the structure

        Returns:
            String representation of the project structure
        """
        structure = f"Project: {node.name}\n"

        def build_tree(node: DirectoryNode, indent: int = 0) -> str:
            result = ""
            indent_str = "    " * indent

            # First output folders
            for child in node.children:
                if isinstance(child, DirectoryNode):
                    result += f"{indent_str}├── {child.name}/\n"
                    result += build_tree(child, indent + 1)

            # Then output files
            for child in node.children:
                if isinstance(child, FileNode):
                    # If we have selected files, only include those
                    if selected_files is None or child.path in selected_files:
                        result += f"{indent_str}├── {child.name}\n"

            return result

        structure += build_tree(node)
        return structure

    def _process_files_from_tree(
        self,
        node: DirectoryNode,
        selected_files: list[str] | None,
        files: list[dict],
        filters: FilterSettings,
    ):
        """
        Recursively process files from the directory tree.

        Args:
            node: Current node in the tree
            selected_files: List of selected files (if None, process all)
            files: List to append processed files to
            filters: Filter settings for file processing
        """
        for child in node.children:
            if isinstance(child, DirectoryNode):
                self._process_files_from_tree(child, selected_files, files, filters)
            elif isinstance(child, FileNode):
                # Skip if we have selected files and this file is not in the list
                if selected_files is not None and child.path not in (selected_files or []):
                    continue

                # Skip binary files
                if child.is_binary:
                    continue

                # Read file content
                try:
                    with open(child.path, encoding="utf-8") as file:
                        file_content = file.read()

                    files.append({"path": child.path, "code": file_content})
                except UnicodeDecodeError:
                    # Skip files with encoding issues
                    pass
                except Exception as e:
                    # Log warning but continue processing other files
                    print(f"Skipping file {os.path.basename(child.path)}: {str(e)}")

    def generate_and_save_documentation(
        self,
        project_path: str,
        template_name: str,
        filters: FilterSettings,
        reference_url: str | None = None,
    ) -> str:
        """
        Generate documentation for a project and save it to the history repository.

        Args:
            project_path: Path to the project directory
            template_name: Name of the template to use for generation
            filters: Filter settings for file selection and processing
            reference_url: Optional reference URL to include in the documentation

        Returns:
            Generated markdown content

        Raises:
            ValueError: If project_path is invalid or template not found
            Exception: If there's an error saving to the repository
        """
        # Validate inputs
        if not project_path or not os.path.isdir(project_path):
            raise ValueError("Project path must be a valid directory")

        template = self._load_template(template_name)
        if not template:
            raise ValueError(f"Template {template_name} not found.")

        # Initialize variables
        files: list[dict] = []
        file_count = 0
        project_structure = ""

        # Get selected files from filters if they exist
        selected_files = None
        if hasattr(filters, "selected_files") and filters.selected_files:
            selected_files = list(filters.selected_files)

        if selected_files:
            # Создаем экземпляр ProjectTreeBuilder
            builder = ProjectTreeBuilder()

            # Строим дерево проекта с выбранными файлами
            root_node = builder.build_tree(project_path, filters)

            if root_node is not None:
                # Собираем структуру проекта и содержимое файлов
                project_structure = self._build_project_structure_from_tree(
                    root_node, selected_files
                )

                # Проходим по всем файлам в дереве
                self._process_files_from_tree(
                    root_node, selected_files, files, filters
                )
            else:
                project_structure = "Error: Could not build project tree."

            # Считаем количество обработанных файлов
            file_count = len(files)
        else:
            # Fallback to legacy behavior - process all files in project
            builder = ProjectTreeBuilder()
            root_node = builder.build_tree(project_path, filters)

            if root_node is not None:
                # Собираем структуру проекта
                project_structure = self._build_project_structure_from_tree(root_node)

                # Проходим по всем файлам в дереве
                self._process_files_from_tree(root_node, None, files, filters)
            else:
                project_structure = "Error: Could not build project tree."

            # Считаем количество обработанных файлов
            file_count = len(files)

        # Prepare context for template
        context = {
            "absolute_code_path": os.path.basename(os.path.abspath(project_path)),
            "source_tree": project_structure,
            "files": files,
        }

        # Generate markdown content
        markdown_content = template(context)
        markdown_content = html.unescape(markdown_content)

        # Create GenerationRequest object
        request = GenerationRequest(
            id=None,
            project_path=project_path,
            project_name=os.path.basename(os.path.abspath(project_path))
            if project_path
            else "Unknown",
            template_name=template_name,
            markdown_content=markdown_content,
            reference_url=reference_url,
            processed_at=datetime.now(),
            file_count=file_count,
            filter_settings=filters,
        )

        # Save to repository
        try:
            self._history_repo.save(request)
        except Exception as e:
            raise Exception(f"Error saving request to database: {str(e)}")

        return markdown_content
