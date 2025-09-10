"""Test data factories for E2E tests."""

import random
import string
from datetime import datetime
from pathlib import Path


class TestDataFactory:
    """Base factory for creating test data."""

    def __init__(self, seed: int | None = None):
        """Initialize the factory with optional seed for reproducible data."""
        if seed is not None:
            random.seed(seed)

    def generate_unique_id(self, prefix: str = "test") -> str:
        """Generate a unique identifier.

        Args:
            prefix: Prefix for the ID

        Returns:
            Unique identifier string
        """
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_suffix = "".join(
            random.choices(string.ascii_lowercase + string.digits, k=6)
        )
        return f"{prefix}_{timestamp}_{random_suffix}"

    def generate_random_string(self, length: int = 10, charset: str = None) -> str:
        """Generate a random string.

        Args:
            length: Length of the string
            charset: Character set to use (defaults to alphanumeric)

        Returns:
            Random string
        """
        if charset is None:
            charset = string.ascii_letters + string.digits
        return "".join(random.choices(charset, k=length))


class PythonFileFactory(TestDataFactory):
    """Factory for creating Python test files."""

    def create_simple_function(self, name: str = None) -> str:
        """Create a simple Python function.

        Args:
            name: Function name (auto-generated if not provided)

        Returns:
            Python code as string
        """
        name = name or f"function_{self.generate_random_string(5)}"
        return f'''def {name}():
    """A simple test function."""
    return "Hello, World!"
'''

    def create_class_with_methods(
        self, class_name: str = None, method_count: int = 3
    ) -> str:
        """Create a Python class with methods.

        Args:
            class_name: Class name (auto-generated if not provided)
            method_count: Number of methods to create

        Returns:
            Python code as string
        """
        class_name = class_name or f"TestClass_{self.generate_random_string(5)}"

        methods = []
        for i in range(method_count):
            method_name = f"method_{i+1}"
            methods.append(f'''    def {method_name}(self):
        """Method {i+1} documentation."""
        return "Method {i+1} called"''')

        return f'''class {class_name}:
    """A test class with multiple methods."""
    
{chr(10).join(methods)}
'''

    def create_complex_file(self, filename: str = None) -> str:
        """Create a complex Python file with multiple components.

        Args:
            filename: Filename for reference (not used in content)

        Returns:
            Python code as string
        """
        return '''import os
import sys
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class User:
    """User data class."""
    id: int
    name: str
    email: str
    
class UserManager:
    """Manages user operations."""
    
    def __init__(self):
        self.users: Dict[int, User] = {}
    
    def add_user(self, user: User) -> bool:
        """Add a new user."""
        if user.id in self.users:
            return False
        self.users[user.id] = user
        return True
    
    def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return self.users.get(user_id)
    
    def list_users(self) -> List[User]:
        """List all users."""
        return list(self.users.values())
    
    def delete_user(self, user_id: int) -> bool:
        """Delete user by ID."""
        if user_id in self.users:
            del self.users[user_id]
            return True
        return False

def main():
    """Main function."""
    manager = UserManager()
    
    # Create some test users
    users = [
        User(1, "Alice", "alice@example.com"),
        User(2, "Bob", "bob@example.com"),
        User(3, "Charlie", "charlie@example.com")
    ]
    
    for user in users:
        manager.add_user(user)
    
    # List all users
    all_users = manager.list_users()
    print(f"Total users: {len(all_users)}")
    
    for user in all_users:
        print(f"User: {user.name} ({user.email})")

if __name__ == "__main__":
    main()
'''

    def create_invalid_python_file(self) -> str:
        """Create an invalid Python file for testing error handling.

        Returns:
            Invalid Python code as string
        """
        return '''def broken_function(
    """This function has syntax errors."""
    return "This won't work"
    
class BrokenClass
    def method(
        return "Missing colon and parameters"
'''

    def save_file(self, content: str, filepath: Path) -> None:
        """Save content to a file.

        Args:
            content: Content to save
            filepath: Path to save to
        """
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text(content, encoding="utf-8")


class TestDataManager:
    """Manages test data creation and cleanup.

    This is a utility class, not a test class.
    """

    def __init__(self, base_dir: Path = None):
        """Initialize the test data manager.

        Args:
            base_dir: Base directory for test data (defaults to temp directory)
        """
        self.base_dir = base_dir or Path("test-results/test-data")
        self.created_files: list[Path] = []

    def create_test_file(
        self, filename: str, content: str = None, factory: PythonFileFactory = None
    ) -> Path:
        """Create a test file.

        Args:
            filename: Name of the file
            content: Content for the file (auto-generated if not provided)
            factory: Factory to use for content generation

        Returns:
            Path to the created file
        """
        factory = factory or PythonFileFactory()
        filepath = self.base_dir / filename

        if content is None:
            content = factory.create_complex_file(filename)

        factory.save_file(content, filepath)
        self.created_files.append(filepath)
        return filepath

    def create_multiple_test_files(
        self, count: int = 3, prefix: str = "test"
    ) -> list[Path]:
        """Create multiple test files.

        Args:
            count: Number of files to create
            prefix: Prefix for filenames

        Returns:
            List of created file paths
        """
        factory = PythonFileFactory()
        files = []

        for i in range(count):
            filename = f"{prefix}_file_{i+1}.py"
            if i == 0:
                content = factory.create_simple_function(f"test_function_{i+1}")
            elif i == 1:
                content = factory.create_class_with_methods(f"TestClass_{i+1}", 2)
            else:
                content = factory.create_complex_file(filename)

            filepath = self.create_test_file(filename, content, factory)
            files.append(filepath)

        return files

    def cleanup_all(self) -> None:
        """Clean up all created test files."""
        for filepath in self.created_files:
            try:
                if filepath.exists():
                    filepath.unlink()
            except Exception as e:
                print(f"Warning: Could not delete {filepath}: {e}")

        # Try to remove empty directories
        try:
            if self.base_dir.exists() and not any(self.base_dir.iterdir()):
                self.base_dir.rmdir()
        except Exception:
            pass  # Ignore if directory is not empty or can't be removed

        self.created_files.clear()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup files."""
        self.cleanup_all()


# Predefined test data templates
TEST_DATA_TEMPLATES = {
    "simple_function": '''def greet(name: str) -> str:
    """Greet a user."""
    return f"Hello, {name}!"
''',
    "simple_class": '''class Calculator:
    """Simple calculator class."""
    
    def add(self, a: float, b: float) -> float:
        """Add two numbers."""
        return a + b
    
    def multiply(self, a: float, b: float) -> float:
        """Multiply two numbers."""
        return a * b
''',
    "complex_module": '''"""
Advanced data processing module.
Provides utilities for data transformation and analysis.
"""

import json
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DataPoint:
    """Represents a single data point."""
    id: int
    value: float
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)

class DataProcessor:
    """Processes and transforms data points."""
    
    def __init__(self, name: str):
        """Initialize the processor.
        
        Args:
            name: Name of the processor
        """
        self.name = name
        self.data_points: List[DataPoint] = []
        logger.info(f"Initialized DataProcessor: {name}")
    
    def add_data_point(self, data_point: DataPoint) -> None:
        """Add a data point to the processor.
        
        Args:
            data_point: Data point to add
        """
        self.data_points.append(data_point)
        logger.debug(f"Added data point: {data_point.id}")
    
    def process_data(self) -> Dict[str, Any]:
        """Process all data points and return statistics.
        
        Returns:
            Dictionary containing processing results
        """
        if not self.data_points:
            return {"error": "No data points to process"}
        
        values = [dp.value for dp in self.data_points]
        
        return {
            "count": len(self.data_points),
            "min": min(values),
            "max": max(values),
            "average": sum(values) / len(values),
            "total": sum(values)
        }
    
    def export_results(self, filename: str) -> bool:
        """Export processing results to a file.
        
        Args:
            filename: Name of the output file
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            results = self.process_data()
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2)
            logger.info(f"Results exported to {filename}")
            return True
        except Exception as e:
            logger.error(f"Export failed: {e}")
            return False

def main():
    """Demonstrate the module functionality."""
    processor = DataProcessor("demo_processor")
    
    # Create sample data
    for i in range(5):
        dp = DataPoint(
            id=i+1,
            value=float(i * 10 + 5),
            metadata={"source": "demo", "index": i}
        )
        processor.add_data_point(dp)
    
    # Process and display results
    results = processor.process_data()
    print("Processing Results:")
    print(json.dumps(results, indent=2))
    
    # Export results
    processor.export_results("demo_results.json")

if __name__ == "__main__":
    main()
''',
}
