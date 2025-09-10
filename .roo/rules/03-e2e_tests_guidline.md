# E2E Testing Quality Guideline

1. **Philosophy & Scope**

      * **Focus on Critical Journeys:** E2E tests must validate critical user workflows from start to finish (e.g., user registration -\> login -\> purchase).     \* **Avoid Exhaustive Testing:** Do not use E2E tests to check every single validation rule or UI state; that is the role of unit and integration tests. E2E tests confirm that integrated components work together correctly.

2. **Tooling & Setup**

      * **Frameworks:** Use **Pytest** as the test runner and **Playwright** for browser automation and control.
      * **Installation:** Add testing tools as development dependencies.

        ```bash
        # Install testing frameworks
        uv add --dev pytest pytest-playwright

        # Install browser binaries
        uv run playwright install
        ```

3. **Directory Structure & Organization**

      * **Dedicated Directory:** Place all E2E tests within a dedicated `tests/e2e/` directory to separate them from faster unit/integration tests.
      * **Page Object Model (POM):** Structure tests using the Page Object Model to improve maintainability and reduce code duplication.

        ```text
        project/
        ├── src/
        └── tests/
            ├── unit/          # Unit tests
            └── e2e/           # E2E tests
                ├── pages/     # Page objects (e.g., login_page.py)
                ├── data/      # Test data files (e.g., users.json)
                └── test_critical_flows.py
        ```

4. **Test Design & Implementation**

      * **Data Isolation:** Tests **must** be independent and isolated. Each test should create its own required data (e.g., create a new user via API before testing login) or use a dedicated, clean test environment. Never rely on hardcoded data that can be altered by other tests.
      * **Clear Naming:** Name test functions descriptively, following the pattern `test_action_with_expected_outcome()` (e.g., `test_login_with_valid_credentials_succeeds()`).
      * **No Hardcoded Waits:** Forbid the use of fixed delays (`time.sleep()`). Use Playwright's built-in web-first assertions and auto-waiting mechanisms (`expect(locator).to_be_visible()`) to handle dynamic content.

5. **Selectors & Locators**

      * **Prioritize Robust Selectors:** Use a clear priority order for selecting elements to avoid flaky tests.
        1. **User-facing attributes:** Use roles, text, and labels first, as a user would.
        2. **Test-specific attributes:** Use `data-testid` for elements that lack clear user-facing attributes.
        3. **Avoid brittle selectors:** Do not use auto-generated, dynamic CSS classes or complex XPath locators that are likely to change.

6. **Execution & CI/CD Integration**

      * **Local Execution:** Run the E2E test suite locally using a dedicated command.

        ```bash
        uv run pytest tests/e2e/
        ```

      * **CI Pipeline:** Execute E2E tests in a dedicated stage in the CI/CD pipeline, typically after the application has been successfully deployed to a staging or preview environment.
      * **Artifacts on Failure:** Configure the CI job to automatically capture Playwright traces, videos, and screenshots as artifacts when a test fails to simplify debugging.

7. **Maintenance & Debugging**

      * **Trace Viewer:** Use Playwright's Trace Viewer to debug failed test runs. It provides a complete, time-traveling view of the test execution.

        ```bash
        # Run tests with tracing enabled
        uv run pytest tests/e2e/ --tracing on

        # Open the trace file for a failed test
        uv run playwright show-trace trace.zip
        ```

      * **Flaky Test Management:** Actively monitor the test suite for flaky tests (tests that pass and fail intermittently without code changes). Isolate, investigate, and fix them immediately or remove them from the main execution pipeline to prevent disruptions.
