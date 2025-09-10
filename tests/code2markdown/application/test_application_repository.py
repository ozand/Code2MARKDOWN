import unittest
from abc import ABC

from code2markdown.application.repository import IHistoryRepository


class TestIHistoryRepository(unittest.TestCase):
    """Test cases for the IHistoryRepository abstract base class."""

    def test_is_abstract_base_class(self):
        """Test that IHistoryRepository is an abstract base class."""
        # Check that IHistoryRepository is an abstract base class
        self.assertTrue(issubclass(IHistoryRepository, ABC))

        # Check that it cannot be instantiated directly
        with self.assertRaises(TypeError):
            IHistoryRepository()

    def test_has_required_abstract_methods(self):
        """Test that IHistoryRepository has all required abstract methods."""
        # Get all abstract methods
        abstract_methods = getattr(IHistoryRepository, "__abstractmethods__", set())

        # Check that all required methods are present
        required_methods = {"save", "get_all", "delete"}
        self.assertEqual(abstract_methods, required_methods)

    def test_method_signatures(self):
        """Test that abstract methods have the correct signatures."""
        # Check that save method is abstract
        save_method = IHistoryRepository.save
        self.assertTrue(hasattr(save_method, "__isabstractmethod__"))
        self.assertTrue(save_method.__isabstractmethod__)

        # Check that get_all method is abstract
        get_all_method = IHistoryRepository.get_all
        self.assertTrue(hasattr(get_all_method, "__isabstractmethod__"))
        self.assertTrue(get_all_method.__isabstractmethod__)

        # Check that delete method is abstract
        delete_method = IHistoryRepository.delete
        self.assertTrue(hasattr(delete_method, "__isabstractmethod__"))
        self.assertTrue(delete_method.__isabstractmethod__)


if __name__ == "__main__":
    unittest.main()
