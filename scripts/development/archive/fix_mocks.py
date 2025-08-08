# Script to fix mocks in test_generation_service.py

# Define the old and new mock patterns
old_mock = """            with patch('pybars.Compiler') as mock_compiler:
                mock_template = Mock()
                mock_template.return_value = "# Generated Documentation\\nContent here"
                mock_compiler.return_value.compile.return_value = mock_template"""

new_mock = """            with patch('pybars.Compiler') as mock_compiler_class:
                mock_compiler_instance = mock_compiler_class.return_value
                mock_template = Mock()
                mock_template.return_value = "# Generated Documentation\\nContent here"
                mock_compiler_instance.compile.return_value = mock_template"""

# Read the file
with open("tests/code2markdown/test_generation_service.py", encoding="utf-8") as f:
    content = f.read()

# Replace the old mock with the new one
content = content.replace(old_mock, new_mock)

# Write the fixed content back to the file
with open("tests/code2markdown/test_generation_service.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Mocks fixed successfully.")
