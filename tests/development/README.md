# Development Scripts Testing Framework

This directory contains comprehensive tests for all development scripts in the `scripts/development/` directory, following the project's testing guidelines and best practices.

## Overview

The testing framework provides:

- **Unit Tests**: Isolated testing of individual functions and methods
- **Integration Tests**: End-to-end testing of script workflows
- **Mock Testing**: Comprehensive use of unittest.mock for test isolation
- **Fixture-Based Testing**: Reusable test data and configurations
- **Performance Testing**: Benchmarks for large dataset handling
- **Error Handling**: Comprehensive error scenario testing

## Test Structure

```
tests/development/
├── __init__.py                 # Package initialization
├── conftest.py                 # Shared fixtures and test utilities
├── test_utils.py              # Unit tests for utils.py (456 lines)
├── test_parser_script.py      # Integration tests for parser_script.py (367 lines)
├── test_validate_kb.py        # Tests for validate_kb.py validation logic (456 lines)
├── test_log_analyzer.py       # Tests for log_analyzer.py capabilities (367 lines)
└── test_generate_logseq_config.py # Tests for generate_logseq_config.py (367 lines)
```

## Key Features

### Comprehensive Fixtures (conftest.py)

- **temp_dir**: Temporary directory fixture for isolated file operations
- **mock_logger**: Mock logger for testing logging functionality
- **sample_project_structure**: Complete project structure for integration tests
- **sample_markdown_content**: Various markdown content types for testing
- **TestHelpers class**: Reusable test operations and utilities

### Test Coverage Areas

#### Utils Module (test_utils.py - 456 lines)
- ScriptUtils class methods (setup_logging, file operations, user interaction)
- Error handling scenarios
- File system operations with backup functionality
- User input validation and prompting
- Tool validation and Python version checking

#### Parser Script (test_parser_script.py - 367 lines)
- End-to-end parsing workflows
- Multiple documentation block formats
- Error handling for missing files
- Dry-run functionality testing
- Real-world content scenarios

#### Validate KB (test_validate_kb.py - 456 lines)
- Link integrity validation
- File structure compliance checking
- Properties schema validation
- Status correctness verification
- README title integrity checks

#### Log Analyzer (test_log_analyzer.py - 367 lines)
- Log parsing and analysis capabilities
- Error detection and reporting
- Performance metrics extraction
- Multi-format log support
- Statistical analysis features

#### Generate Logseq Config (test_generate_logseq_config.py - 367 lines)
- Configuration file generation
- Template processing and validation
- Error handling for invalid inputs
- Integration with project structure
- Configuration validation and testing

## Running Tests

### Run All Development Script Tests
```bash
uv run pytest tests/development/
```

### Run Specific Test Categories
```bash
# Unit tests only
uv run pytest tests/development/ -m unit

# Integration tests only
uv run pytest tests/development/ -m integration

# Development scripts tests
uv run pytest tests/development/ -m development_scripts
```

### Run Tests with Coverage
```bash
uv run pytest tests/development/ --cov=scripts --cov-report=html --cov-report=term
```

### Run Tests with Specific Markers
```bash
# Utils module tests
uv run pytest tests/development/ -m utils

# Parser module tests
uv run pytest tests/development/ -m parser

# Validator module tests
uv run pytest tests/development/ -m validator

# Log analyzer tests
uv run pytest tests/development/ -m log_analyzer

# Config generator tests
uv run pytest tests/development/ -m config_generator
```

## Test Configuration

The tests are configured through [`pyproject.toml`](../../pyproject.toml) with:

- **Coverage reporting** for both src and scripts directories
- **Test markers** for categorizing different test types
- **Pytest configuration** optimized for development script testing

## Mock Testing Strategy

The framework extensively uses `unittest.mock` for:

- **File system operations**: Mocking `os`, `shutil`, and file I/O operations
- **Subprocess calls**: Mocking `subprocess.run` and related functions
- **User input**: Mocking `input()` function for interactive scripts
- **Logging**: Mocking logging to capture and verify log messages
- **External dependencies**: Isolating tests from external system calls

## Performance Testing

Tests include performance benchmarks for:

- **Large file processing**: Testing scripts with large datasets
- **Memory usage**: Monitoring memory consumption during operations
- **Execution time**: Measuring performance of critical operations
- **Scalability**: Testing behavior with increasing data sizes

## Error Handling Testing

Comprehensive error scenario testing includes:

- **File not found errors**: Testing graceful handling of missing files
- **Permission errors**: Testing behavior with restricted file access
- **Invalid input errors**: Testing validation and error reporting
- **Network errors**: Testing behavior with failed network operations
- **Configuration errors**: Testing handling of invalid configurations

## Best Practices

### Test Independence
- Each test is completely isolated and independent
- Tests create their own temporary directories and files
- No reliance on external system state

### Clear Naming
- Test functions follow descriptive naming patterns
- Test data is clearly labeled and organized
- Fixtures are well-documented with docstrings

### Comprehensive Coverage
- Tests cover both success and failure scenarios
- Edge cases are thoroughly tested
- Performance characteristics are validated

### Maintainability
- Tests are organized logically by module
- Common functionality is extracted into fixtures
- Test data is reusable and well-structured

## Continuous Integration

The tests are integrated into the CI/CD pipeline with:

- **Automated test execution** on every commit
- **Coverage reporting** to track test coverage
- **Performance monitoring** to detect regressions
- **Error reporting** with detailed failure information

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure proper PYTHONPATH configuration
2. **Mock conflicts**: Check for conflicting mock setups
3. **File permission issues**: Use temporary directories for file operations
4. **Performance issues**: Use appropriate test data sizes

### Debug Mode

Run tests with verbose output for debugging:
```bash
uv run pytest tests/development/ -v --tb=short
```

### Coverage Reports

View detailed coverage reports:
```bash
# Generate HTML coverage report
uv run pytest tests/development/ --cov=scripts --cov-report=html
# Open in browser
open htmlcov/index.html
```

## Contributing

When adding new tests:

1. Follow the existing test structure and patterns
2. Use appropriate fixtures from `conftest.py`
3. Include both positive and negative test cases
4. Add proper documentation and docstrings
5. Ensure tests are independent and isolated
6. Update this README with new test information

## Future Enhancements

- **Parallel test execution** for faster test runs
- **Property-based testing** for more comprehensive coverage
- **Visual regression testing** for UI-related scripts
- **Load testing** for performance-critical scripts
- **Integration with external testing services**

This testing framework ensures that all development scripts are thoroughly tested, reliable, and maintainable, following the project's quality standards and best practices.