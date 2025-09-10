"""Configuration and fixtures for E2E tests using Playwright."""

import os
import pytest
from pathlib import Path
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page


@pytest.fixture(scope="session")
def playwright_instance():
    """Create a Playwright instance for the test session."""
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="session")
def browser(playwright_instance, pytestconfig):
    """Create a browser instance for the test session."""
    browser_type = pytestconfig.getoption("--browser", default="chromium")
    
    browser = getattr(playwright_instance, browser_type).launch(
        headless=not pytestconfig.getoption("--headed", default=False),
        args=["--no-sandbox", "--disable-dev-shm-usage"]  # For CI environments
    )
    yield browser
    browser.close()


@pytest.fixture
def context(browser: Browser, pytestconfig):
    """Create a new browser context for each test."""
    # Configure tracing if enabled
    trace_dir = Path("test-results/traces")
    trace_dir.mkdir(parents=True, exist_ok=True)
    
    context = browser.new_context(
        viewport={"width": 1280, "height": 720},
        locale="en-US",
        record_video_dir="test-results/videos" if pytestconfig.getoption("--tracing", default=False) else None,
        record_video_size={"width": 1280, "height": 720},
    )
    
    # Start tracing if enabled
    if pytestconfig.getoption("--tracing", default=False):
        context.tracing.start(
            screenshots=True,
            snapshots=True,
            sources=True
        )
    
    yield context
    
    # Stop tracing and save trace if enabled
    if pytestconfig.getoption("--tracing", default=False):
        trace_path = trace_dir / f"{pytestconfig.getoption('current_test_name', 'unknown')}.zip"
        context.tracing.stop(path=str(trace_path))
    
    context.close()


@pytest.fixture
def page(context: BrowserContext):
    """Create a new page for each test."""
    page = context.new_page()
    yield page
    page.close()


@pytest.fixture
def base_url(pytestconfig):
    """Get the base URL for the application."""
    return pytestconfig.getoption("--base-url") or os.getenv("BASE_URL", "http://localhost:8000")


@pytest.fixture(autouse=True)
def setup_test_result_directory():
    """Set up test result directories."""
    test_results = Path("test-results")
    test_results.mkdir(exist_ok=True)
    
    # Create subdirectories
    (test_results / "screenshots").mkdir(exist_ok=True)
    (test_results / "videos").mkdir(exist_ok=True)
    (test_results / "traces").mkdir(exist_ok=True)
    
    yield


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "e2e: marks tests as end-to-end tests"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add custom markers."""
    for item in items:
        # Add e2e marker to all tests in this directory
        if "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)