"""
Script to update imports in test files to match the new project structure.
"""

import os
import re


def update_imports_in_file(file_path):
    """Update imports in a single file."""
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # Replace 'from src.code2markdown.' with 'from code2markdown.'
    content = re.sub(r"from src\.code2markdown\.", "from code2markdown.", content)
    # Replace 'from src.code2markdown import' with 'from code2markdown import'
    content = re.sub(
        r"from src\.code2markdown import", "from code2markdown import", content
    )
    # Replace 'import src.code2markdown.' with 'import code2markdown.'
    content = re.sub(r"import src\.code2markdown\.", "import code2markdown.", content)

    # Replace 'from app import' with 'from code2markdown.app import'
    content = re.sub(r"from app import", "from code2markdown.app import", content)
    # Replace 'import app' with 'import code2markdown.app'
    content = re.sub(r"import app", "import code2markdown.app", content)

    # Replace 'from domain.' with 'from code2markdown.domain.'
    content = re.sub(r"from domain\.", "from code2markdown.domain.", content)
    # Replace 'from domain import' with 'from code2markdown.domain import'
    content = re.sub(r"from domain import", "from code2markdown.domain import", content)
    # Replace 'import domain.' with 'import code2markdown.domain.'
    content = re.sub(r"import domain\.", "import code2markdown.domain.", content)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


def main():
    """Main function."""
    # Define the root directory of the project
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Define the directories to search for test files
    test_dirs = [
        os.path.join(root_dir, "tests", "code2markdown"),
        os.path.join(root_dir, "tests", "performance"),
    ]

    # Define the files in the root directory to update
    root_test_files = [
        os.path.join(root_dir, "test_simple.py"),
    ]

    # Update imports in test files in test directories
    for test_dir in test_dirs:
        if os.path.exists(test_dir):
            for root, _, files in os.walk(test_dir):
                for file in files:
                    if file.startswith("test_") and file.endswith(".py"):
                        file_path = os.path.join(root, file)
                        print(f"Updating imports in {file_path}")
                        update_imports_in_file(file_path)

    # Update imports in test files in the root directory
    for file_path in root_test_files:
        if os.path.exists(file_path):
            print(f"Updating imports in {file_path}")
            update_imports_in_file(file_path)

    print("Import updates completed.")


if __name__ == "__main__":
    main()
