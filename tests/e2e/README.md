# E2E Testing Documentation

This directory contains the End-to-End (E2E) testing infrastructure for the Code2Markdown application, following the guidelines in [`rules.e2e-tests-guidline`](../../pages/rules.e2e-tests-guidline.md).

## Overview

The E2E test suite validates critical user workflows for the Code2Markdown application, ensuring that:
- Users can upload Python files
- The application correctly processes and converts code to markdown
- Generated documentation is accurate and complete
- The UI is responsive and accessible
- Error handling works properly

## Architecture

### Directory Structure
```
tests/e2e/
├── conftest.py              # Test configuration and fixtures
├── test_critical_flows.py   # Main E2E test cases
├── pages/                   # Page Object Model classes
│   ├── __init__.py
│   ├── base_page.py        # Base page with common functionality
│   └── main_page.py        # Main application page
└── data/                   # Test data management
    ├── __init__.py
    └── factories.py        # Test data factories
```

### Key Components

#### 1. Page Object Model (POM)
- **BasePage**: Abstract base class with common page functionality
- **MainPage**: Specific implementation for the main application page
- Provides robust element selection and interaction methods
- Supports multiple locator strategies (ARIA, text, test-id)

#### 2. Test Data Management
- **TestDataManager**: Context manager for creating and cleaning up test files
- **PythonFileFactory**: Generates various types of Python test files
- **Predefined Templates**: Ready-to-use test data templates

#### 3. Configuration Management
- Multi-browser support (Chromium, Firefox, WebKit)
- Configurable tracing, video recording, and screenshots
- Environment variable support for different deployment environments

## Running Tests

### Local Execution

```bash
# Run all E2E tests
uv run pytest tests/e2e/

# Run with specific browser
uv run pytest tests/e2e/ --browser chromium

# Run in headed mode (visible browser)
uv run pytest tests/e2e/ --headed

# Run with tracing enabled
uv run pytest tests/e2e/ --tracing on

# Run specific test
uv run pytest tests/e2e/test_critical_flows.py::TestCriticalFlows::test_basic_file_conversion_flow

# Run with video recording
uv run pytest tests/e2e/ --video retain-on-failure

# Run with screenshots on failure
uv run pytest tests/e2e/ --screenshot only-on-failure
```

### Environment Variables

```bash
# Set base URL for the application
export BASE_URL=http://localhost:8000

# Set default browser
export PLAYWRIGHT_BROWSER=chromium

# Set headed mode
export PLAYWRIGHT_HEADED=false

# Set timeout values
export PLAYWRIGHT_TIMEOUT=30000
```

### Command Line Options

The test suite supports several command-line options:

- `--browser`: Choose browser (chromium, firefox, webkit, all)
- `--headed`: Run tests in headed mode
- `--tracing`: Enable tracing (on, off, retain-on-failure)
- `--video`: Video recording (on, off, retain-on-failure)
- `--screenshot`: Screenshot capture (on, off, only-on-failure)
- `--slowmo`: Add delay between actions (milliseconds)
- `--output`: Output directory for artifacts

## Test Cases

### Critical Flows Covered

1. **Basic File Conversion**: Upload single Python file and generate markdown
2. **Multiple File Upload**: Handle multiple files concurrently
3. **Class Documentation**: Generate documentation for Python classes
4. **Complex Module Processing**: Handle modules with multiple components
5. **Error Handling**: Graceful handling of invalid files
6. **File Filtering**: Only process Python files, ignore others
7. **UI Navigation**: Test basic UI elements and navigation
8. **Responsive Design**: Test across different viewport sizes
9. **Download Functionality**: Test markdown download feature
10. **Clear/Reset**: Test application reset functionality
11. **Template Variations**: Test different Python code patterns
12. **Edge Cases**: Empty files, large files, concurrent processing

### Test Data Templates

The test suite includes predefined templates for different Python code patterns:

- **Simple Function**: Basic function with docstring
- **Simple Class**: Class with methods and documentation
- **Complex Module**: Advanced module with multiple components

## Debugging

### Using Playwright Trace Viewer

When tests fail with tracing enabled, you can debug using the trace viewer:

```bash
# Run tests with tracing
uv run pytest tests/e2e/ --tracing on

# Open trace viewer for a specific test
uv run playwright show-trace test-results/test_critical_flows-py-test-basic-file-conversion-flow-chromium/trace.zip
```

### Analyzing Test Artifacts

Test artifacts are automatically collected on failure:
- **Screenshots**: Captured at the point of failure
- **Videos**: Full test execution recording
- **Traces**: Detailed step-by-step execution log
- **Console Logs**: Browser console output

### Common Issues and Solutions

1. **Element Not Found**: Use more robust selectors (ARIA roles, text content)
2. **Timeout Errors**: Increase timeout values or add explicit waits
3. **File Upload Issues**: Verify file paths and upload mechanism
4. **Browser Compatibility**: Test across different browsers
5. **CI/CD Failures**: Check environment setup and dependencies

## CI/CD Integration

The test suite includes GitHub Actions workflows for automated testing:

- **PR Testing**: Runs on pull requests
- **Main Branch Testing**: Runs on pushes to main/develop
- **Scheduled Testing**: Daily test execution
- **Multi-browser Testing**: Tests across Chromium, Firefox, WebKit
- **Artifact Collection**: Automatic collection of test artifacts
- **Failure Notifications**: GitHub issues created for test failures

### Workflow Configuration

The workflow supports manual dispatch with options:
- Browser selection
- Headed/headless mode
- Tracing configuration
- Custom test parameters

## Best Practices

### Test Design
- Use descriptive test names following the pattern `test_action_with_expected_outcome()`
- Keep tests independent and isolated
- Use the Page Object Model for maintainability
- Implement proper setup and teardown

### Element Selection
1. Prefer user-facing attributes (roles, text, labels)
2. Use test-specific attributes (`data-testid`) when needed
3. Avoid brittle selectors (dynamic CSS classes, complex XPath)

### Performance
- Use Playwright's auto-waiting mechanisms
- Avoid hardcoded waits (`time.sleep()`)
- Set appropriate timeout values
- Optimize test execution order

### Reliability
- Implement robust error handling
- Use proper assertions with clear messages
- Handle dynamic content appropriately
- Test across different browsers and viewport sizes

## Maintenance

### Adding New Tests
1. Create test method in `test_critical_flows.py`
2. Use existing fixtures and page objects
3. Follow naming conventions
4. Add appropriate assertions
5. Update documentation if needed

### Updating Page Objects
1. Modify relevant page class in `pages/`
2. Maintain backward compatibility
3. Add new methods as needed
4. Update docstrings
5. Test changes thoroughly

### Managing Test Data
1. Use `TestDataManager` for file creation
2. Add new templates to `TEST_DATA_TEMPLATES`
3. Ensure proper cleanup in teardown
4. Document new data patterns

## Troubleshooting

### Local Development Issues
- Ensure Playwright browsers are installed
- Check Python environment setup
- Verify application server is running
- Review browser console for errors

### CI/CD Issues
- Check workflow configuration
- Verify artifact upload/download
- Review environment variables
- Analyze test logs and artifacts

### Test Flakiness
- Use more stable selectors
- Add explicit waits where needed
- Increase timeout values
- Implement retry mechanisms

## Contributing

When adding new E2E tests:
1. Follow existing patterns and conventions
2. Ensure tests are independent and reliable
3. Add appropriate documentation
4. Test across different browsers
5. Update this README with new information

For questions or issues, refer to the project's main documentation or create an issue in the repository.