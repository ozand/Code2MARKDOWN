# Guideline: E2E Testing

## 1. Philosophy & Scope

- **Focus on Critical Journeys:** E2E tests must validate critical user workflows from start to finish.
- **Avoid Exhaustive Testing:** Do not use E2E tests to check every single validation rule or UI state; that is the role of unit and integration tests.

## 2. Tooling & Setup

- **Frameworks:** Use **Pytest** as the test runner and **Playwright** for browser automation.
- **Installation:** `uv add --dev pytest pytest-playwright` followed by `uv run playwright install`.

## 3. Directory Structure & Organization

- **Dedicated Directory:** Place all E2E tests within a dedicated `tests/e2e/` directory.
- **Page Object Model (POM):** Structure tests using the Page Object Model to improve maintainability.

## 4. Test Design & Implementation

- **Data Isolation:** Tests **must** be independent and isolated. Each test should create its own required data.
- **No Hardcoded Waits:** Forbid the use of fixed delays (`time.sleep()`). Use Playwright's built-in web-first assertions and auto-waiting mechanisms.

## 5. Selectors & Locators

- **Prioritize Robust Selectors:** Use a clear priority order:
  1. **User-facing attributes:** roles, text, and labels.
  2. **Test-specific attributes:** `data-testid`.
  3. **Avoid brittle selectors:** dynamic CSS classes or complex XPath.