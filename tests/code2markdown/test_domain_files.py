import os
import tempfile
import unittest

from code2markdown.domain.files import DirectoryNode, FileNode, ProjectTreeBuilder
from code2markdown.domain.filters import FileSize, FilterSettings


class TestFileNode(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.test_file_path = os.path.join(self.test_dir, "test.py")
        self.test_file_size = 1024

        # Create a test file
        with open(self.test_file_path, "w") as f:
            f.write("print('Hello World')")

        self.file_node = FileNode(
            path=self.test_file_path,
            name="test.py",
            size=self.test_file_size,
            is_binary=False,
        )

        self.filters = FilterSettings(
            include_patterns=[".py", ".txt"],
            exclude_patterns=["temp", "cache"],
            max_file_size=FileSize(kb=2),
            show_excluded=False,
        )

    def tearDown(self):
        # Clean up test directory
        import shutil

        shutil.rmtree(self.test_dir)

    def test_is_excluded_by_size(self):
        """Test that file is excluded when it exceeds max file size"""
        # Create a filter with smaller max size
        small_filters = FilterSettings(
            include_patterns=[".py"],
            exclude_patterns=[],
            max_file_size=FileSize(kb=0.5),  # 512 bytes
        )

        self.assertTrue(self.file_node.is_excluded(small_filters))

    def test_is_excluded_by_include_pattern(self):
        """Test that file is excluded when it doesn't match include pattern"""
        # Create a filter that only includes .txt files
        txt_filters = FilterSettings(
            include_patterns=[".txt"], exclude_patterns=[], max_file_size=FileSize(kb=5)
        )

        self.assertTrue(self.file_node.is_excluded(txt_filters))

    def test_is_excluded_by_exclude_pattern(self):
        """Test that file is excluded when it matches exclude pattern"""
        # Create a filter that excludes files with 'test' in name
        exclude_filters = FilterSettings(
            include_patterns=[".py"],
            exclude_patterns=["test"],
            max_file_size=FileSize(kb=5),
        )

        self.assertTrue(self.file_node.is_excluded(exclude_filters))

    def test_is_excluded_by_gitignore(self):
        """Test that file is excluded when it matches .gitignore pattern"""
        # Create a .gitignore file
        gitignore_path = os.path.join(self.test_dir, ".gitignore")
        with open(gitignore_path, "w") as f:
            f.write("*.py\n")

        filters = FilterSettings(
            include_patterns=[".py"], exclude_patterns=[], max_file_size=FileSize(kb=5)
        )

        self.assertTrue(self.file_node.is_excluded(filters))

    def test_is_not_excluded(self):
        """Test that file is not excluded when it passes all filters"""
        self.assertFalse(self.file_node.is_excluded(self.filters))


class TestProjectTreeBuilder(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.builder = ProjectTreeBuilder()

        # Create test directory structure
        # test_dir/
        #   ├── file1.py
        #   ├── file2.txt
        #   ├── excluded.py
        #   ├── temp_file.py
        #   └── subdir/
        #       ├── file3.py
        #       └── cache_file.txt

        # Create files
        self.file1_path = os.path.join(self.test_dir, "file1.py")
        self.file2_path = os.path.join(self.test_dir, "file2.txt")
        self.excluded_path = os.path.join(self.test_dir, "excluded.py")
        self.temp_path = os.path.join(self.test_dir, "temp_file.py")

        with open(self.file1_path, "w") as f:
            f.write("print('file1')")
        with open(self.file2_path, "w") as f:
            f.write("content2")
        with open(self.excluded_path, "w") as f:
            f.write("excluded")
        with open(self.temp_path, "w") as f:
            f.write("temp")

        # Create subdirectory and files
        self.subdir_path = os.path.join(self.test_dir, "subdir")
        os.mkdir(self.subdir_path)

        self.file3_path = os.path.join(self.subdir_path, "file3.py")
        self.cache_path = os.path.join(self.subdir_path, "cache_file.txt")

        with open(self.file3_path, "w") as f:
            f.write("print('file3')")
        with open(self.cache_path, "w") as f:
            f.write("cache")

        self.filters = FilterSettings(
            include_patterns=[".py"],
            exclude_patterns=["temp", "cache"],
            max_file_size=FileSize(kb=1),
        )

    def tearDown(self):
        # Clean up test directory
        import shutil

        shutil.rmtree(self.test_dir)

    def test_build_tree_includes_correct_files(self):
        """Test that build_tree includes only files that pass filters"""
        root_node = self.builder.build_tree(self.test_dir, self.filters)

        # Check that file1.py is included (matches .py pattern, not excluded)
        file1_node = None
        for child in root_node.children:
            if isinstance(child, FileNode) and child.name == "file1.py":
                file1_node = child
                break
        self.assertIsNotNone(file1_node)

        # Check that file2.txt is excluded (doesn't match .py pattern)
        file2_node = None
        for child in root_node.children:
            if isinstance(child, FileNode) and child.name == "file2.txt":
                file2_node = child
                break
        self.assertIsNone(file2_node)

        # Check that temp_file.py is excluded (matches 'temp' pattern)
        temp_node = None
        for child in root_node.children:
            if isinstance(child, FileNode) and child.name == "temp_file.py":
                temp_node = child
                break
        self.assertIsNone(temp_node)

        # Check that excluded.py is included (doesn't match 'temp' pattern)
        excluded_node = None
        for child in root_node.children:
            if isinstance(child, FileNode) and child.name == "excluded.py":
                excluded_node = child
                break
        self.assertIsNotNone(excluded_node)

        # Check that subdir is included
        subdir_node = None
        for child in root_node.children:
            if isinstance(child, DirectoryNode) and child.name == "subdir":
                subdir_node = child
                break
        self.assertIsNotNone(subdir_node)

        # Check that file3.py is included in subdir
        file3_node = None
        if subdir_node:
            for child in subdir_node.children:
                if isinstance(child, FileNode) and child.name == "file3.py":
                    file3_node = child
                    break
        self.assertIsNotNone(file3_node)

        # Check that cache_file.txt is excluded in subdir (matches 'cache' pattern)
        cache_node = None
        if subdir_node:
            for child in subdir_node.children:
                if isinstance(child, FileNode) and child.name == "cache_file.txt":
                    cache_node = child
                    break
        self.assertIsNone(cache_node)

    def test_build_tree_respects_max_depth(self):
        """Test that build_tree respects max_depth parameter"""
        # Create filters with max_depth=1
        filters_depth_one = FilterSettings(
            include_patterns=[".py", ".txt"],
            exclude_patterns=["temp", "cache"],
            max_file_size=FileSize(kb=1),
            max_depth=1,
        )
        # Use a fresh builder to avoid cache issues
        fresh_builder = ProjectTreeBuilder()
        root_node = fresh_builder.build_tree(self.test_dir, filters_depth_one)

        # At max_depth=1, subdir should be included but its contents should not be explored
        subdir_node = None
        for child in root_node.children:
            if isinstance(child, DirectoryNode) and child.name == "subdir":
                subdir_node = child
                break
        self.assertIsNotNone(subdir_node)

        # Subdir should have no children since we didn't explore deeper
        if subdir_node:
            self.assertEqual(len(subdir_node.children), 0)

    def test_build_tree_with_max_depth_none(self):
        """Test that build_tree with max_depth=None has no depth limit"""
        # Create filters with max_depth=None
        filters_no_limit = FilterSettings(
            include_patterns=[".py", ".txt"],
            exclude_patterns=["temp", "cache"],
            max_file_size=FileSize(kb=1),
            max_depth=None,
        )

        root_node = self.builder.build_tree(self.test_dir, filters_no_limit)

        # Check that subdir is included
        subdir_node = None
        for child in root_node.children:
            if isinstance(child, DirectoryNode) and child.name == "subdir":
                subdir_node = child
                break
        self.assertIsNotNone(subdir_node)

        # With no depth limit, subdir should have its children
        if subdir_node:
            # Should have file3.py but not cache_file.txt (excluded by pattern)
            py_files = [
                child
                for child in subdir_node.children
                if isinstance(child, FileNode) and child.name == "file3.py"
            ]
            cache_files = [
                child
                for child in subdir_node.children
                if isinstance(child, FileNode) and child.name == "cache_file.txt"
            ]
            self.assertEqual(len(py_files), 1)
            self.assertEqual(len(cache_files), 0)

    def test_build_tree_with_max_depth_zero(self):
        """Test that build_tree with max_depth=0 returns only root"""
        # Create filters with max_depth=0
        filters_depth_zero = FilterSettings(
            include_patterns=[".py", ".txt"],
            exclude_patterns=["temp", "cache"],
            max_file_size=FileSize(kb=1),
            max_depth=0,
        )

        root_node = self.builder.build_tree(self.test_dir, filters_depth_zero)

        # With max_depth=0, root should have no children
        self.assertEqual(len(root_node.children), 0)

    def test_build_tree_with_max_depth_two(self):
        """Test that build_tree with max_depth=2 explores to second level"""
        # Create filters with max_depth=2
        filters_depth_two = FilterSettings(
            include_patterns=[".py", ".txt"],
            exclude_patterns=["temp", "cache"],
            max_file_size=FileSize(kb=1),
            max_depth=2,
        )

        root_node = self.builder.build_tree(self.test_dir, filters_depth_two)

        # Check that subdir is included
        subdir_node = None
        for child in root_node.children:
            if isinstance(child, DirectoryNode) and child.name == "subdir":
                subdir_node = child
                break
        self.assertIsNotNone(subdir_node)

        # With max_depth=2, subdir should have its children
        if subdir_node:
            # Should have file3.py but not cache_file.txt (excluded by pattern)
            py_files = [
                child
                for child in subdir_node.children
                if isinstance(child, FileNode) and child.name == "file3.py"
            ]
            cache_files = [
                child
                for child in subdir_node.children
                if isinstance(child, FileNode) and child.name == "cache_file.txt"
            ]
            self.assertEqual(len(py_files), 1)
            self.assertEqual(len(cache_files), 0)

        # Create a sub-subdirectory to test depth limit
        subsubdir_path = os.path.join(self.subdir_path, "subsubdir")
        os.mkdir(subsubdir_path)

        # Add a file to the sub-subdirectory
        subsub_file_path = os.path.join(subsubdir_path, "deep_file.py")
        with open(subsub_file_path, "w") as f:
            f.write("print('deep')")

        # Rebuild tree with max_depth=2 using a new builder to avoid cache issues
        fresh_builder = ProjectTreeBuilder()
        root_node = fresh_builder.build_tree(self.test_dir, filters_depth_two)

        # Find the subdir and subsubdir in the new tree
        subdir_node = None
        for child in root_node.children:
            if isinstance(child, DirectoryNode) and child.name == "subdir":
                subdir_node = child
                break
        self.assertIsNotNone(subdir_node)

        # Find the subsubdir
        subsubdir_node = None
        if subdir_node:
            for child in subdir_node.children:
                if isinstance(child, DirectoryNode) and child.name == "subsubdir":
                    subsubdir_node = child
                    break
        self.assertIsNotNone(subsubdir_node)

        # With max_depth=2, subsubdir should exist but have no children (depth limit reached)
        if subsubdir_node:
            self.assertEqual(len(subsubdir_node.children), 0)


class TestDirectoryNode(unittest.TestCase):
    def test_directory_node_creation(self):
        """Test basic DirectoryNode creation and properties"""
        dir_node = DirectoryNode(path="/test/path", name="test_dir")

        self.assertEqual(dir_node.path, "/test/path")
        self.assertEqual(dir_node.name, "test_dir")
        self.assertIsInstance(dir_node.children, list)
        self.assertEqual(len(dir_node.children), 0)

    def test_directory_node_with_children(self):
        """Test DirectoryNode with initial children"""
        file_node = FileNode(
            path="/test/path/file.py", name="file.py", size=100, is_binary=False
        )

        dir_node = DirectoryNode(path="/test/path", name="test_dir", children=[file_node])

        self.assertEqual(len(dir_node.children), 1)
        self.assertEqual(dir_node.children[0], file_node)


if __name__ == "__main__":
    unittest.main()
