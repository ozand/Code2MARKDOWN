# Script to fix specific lines in test_generation_service.py

# Define the lines to be replaced
fixes = [
    # Line 72
    (
        "            with patch('pybars.Compiler') as mock_compiler:\\n                mock_template = Mock()\\n                mock_template.return_value = \\\"# Generated Documentation\\\\nContent here\\\"\\n                mock_compiler.return_value.compile.return_value = mock_template",
        "            with patch('pybars.Compiler') as mock_compiler:\n                mock_template = Mock()\n                mock_template.return_value = \"# Generated Documentation\\nContent here\"\n                mock_compiler.return_value.compile.return_value = mock_template",
    ),
    # Line 143
    (
        "            with patch('pybars.Compiler') as mock_compiler:\\n                mock_template = Mock()\\n                mock_template.return_value = \\\"# Generated Documentation\\\\nContent here\\\"\\n                mock_compiler.return_value.compile.return_value = mock_template",
        "            with patch('pybars.Compiler') as mock_compiler:\n                mock_template = Mock()\n                mock_template.return_value = \"# Generated Documentation\\nContent here\"\n                mock_compiler.return_value.compile.return_value = mock_template",
    ),
    # Line 206
    (
        "            with patch('pybars.Compiler') as mock_compiler:\\n                mock_template = Mock()\\n                mock_template.return_value = \\\"# Generated Documentation\\\\nContent here\\\"\\n                mock_compiler.return_value.compile.return_value = mock_template",
        "            with patch('pybars.Compiler') as mock_compiler:\n                mock_template = Mock()\n                mock_template.return_value = \"# Generated Documentation\\nContent here\"\n                mock_compiler.return_value.compile.return_value = mock_template",
    ),
    # Line 240
    (
        "            with patch('pybars.Compiler') as mock_compiler:\\n                mock_template = Mock()\\n                mock_template.return_value = \\\"# Generated Documentation\\\\nContent here\\\"\\n                mock_compiler.return_value.compile.return_value = mock_template",
        "            with patch('pybars.Compiler') as mock_compiler:\n                mock_template = Mock()\n                mock_template.return_value = \"# Generated Documentation\\nContent here\"\n                mock_compiler.return_value.compile.return_value = mock_template",
    ),
    # Line 273
    (
        "            with patch('pybars.Compiler') as mock_compiler:\\n                mock_template = Mock()\\n                mock_template.return_value = \\\"# Generated Documentation\\\\nContent here\\\"\\n                mock_compiler.return_value.compile.return_value = mock_template",
        "            with patch('pybars.Compiler') as mock_compiler:\n                mock_template = Mock()\n                mock_template.return_value = \"# Generated Documentation\\nContent here\"\n                mock_compiler.return_value.compile.return_value = mock_template",
    ),
]

# Read the file
with open("tests/code2markdown/test_generation_service.py", encoding="utf-8") as f:
    content = f.read()

# Apply fixes
for old, new in fixes:
    content = content.replace(old, new)

# Write the fixed content back to the file
with open("tests/code2markdown/test_generation_service.py", "w", encoding="utf-8") as f:
    f.write(content)

print("File fixed successfully.")
