"""Base page class for E2E tests using Playwright."""

import os
from abc import ABC, abstractmethod
from pathlib import Path

from playwright.sync_api import Locator, Page, expect


class BasePage(ABC):
    """Base class for all page objects."""

    def __init__(self, page: Page, base_url: str = None):
        """Initialize the base page object.

        Args:
            page: Playwright page instance
            base_url: Base URL for the application (defaults to env var or localhost:8501)
        """
        self.page = page
        self.base_url = base_url or os.getenv("E2E_BASE_URL", "http://localhost:8501")
        self.timeout = int(os.getenv("E2E_TIMEOUT", "30000"))

    @property
    @abstractmethod
    def url_path(self) -> str:
        """Return the URL path for this page."""
        pass

    @property
    @abstractmethod
    def page_title(self) -> str:
        """Return the expected page title."""
        pass

    def navigate(self, **kwargs) -> "BasePage":
        """Navigate to the page and wait for it to load.

        Args:
            **kwargs: Additional query parameters to append to the URL

        Returns:
            Self for method chaining
        """
        url = self.base_url + self.url_path
        if kwargs:
            query_params = "&".join(f"{k}={v}" for k, v in kwargs.items())
            url += f"?{query_params}"

        self.page.goto(url)
        self.wait_for_load()
        return self

    def wait_for_load(self) -> None:
        """Wait for the page to load completely."""
        self.page.wait_for_load_state("networkidle")
        # Wait for the page title to be correct
        expect(self.page).to_have_title(self.page_title, timeout=self.timeout)

    def is_loaded(self) -> bool:
        """Check if the page is loaded correctly."""
        try:
            self.page.wait_for_load_state("networkidle", timeout=5000)
            return self.page.title() == self.page_title
        except Exception:
            return False

    def take_screenshot(self, name: str, full_page: bool = True) -> Path:
        """Take a screenshot of the current page.

        Args:
            name: Name for the screenshot file
            full_page: Whether to capture the full page

        Returns:
            Path to the screenshot file
        """
        screenshot_dir = Path("test-results/screenshots")
        screenshot_dir.mkdir(parents=True, exist_ok=True)

        screenshot_path = screenshot_dir / f"{name}.png"
        self.page.screenshot(path=str(screenshot_path), full_page=full_page)
        return screenshot_path

    def wait_for_element(self, selector: str, timeout: int | None = None) -> Locator:
        """Wait for an element to be visible.

        Args:
            selector: CSS selector for the element
            timeout: Timeout in milliseconds (defaults to page timeout)

        Returns:
            Locator for the element
        """
        timeout = timeout or self.timeout
        element = self.page.locator(selector)
        element.wait_for(state="visible", timeout=timeout)
        return element

    def get_element_by_role(self, role: str, name: str = None, **kwargs) -> Locator:
        """Get an element by its ARIA role.

        Args:
            role: ARIA role (button, link, textbox, etc.)
            name: Accessible name of the element
            **kwargs: Additional filters

        Returns:
            Locator for the element
        """
        return self.page.get_by_role(role, name=name, **kwargs)

    def get_element_by_text(self, text: str, exact: bool = False) -> Locator:
        """Get an element by its text content.

        Args:
            text: Text to search for
            exact: Whether to match exactly

        Returns:
            Locator for the element
        """
        return self.page.get_by_text(text, exact=exact)

    def get_element_by_test_id(self, test_id: str) -> Locator:
        """Get an element by its data-testid attribute.

        Args:
            test_id: Value of the data-testid attribute

        Returns:
            Locator for the element
        """
        return self.page.get_by_test_id(test_id)

    def expect_element_to_be_visible(
        self, selector: str, timeout: int | None = None
    ) -> None:
        """Expect an element to be visible.

        Args:
            selector: CSS selector for the element
            timeout: Timeout in milliseconds
        """
        element = self.page.locator(selector)
        expect(element).to_be_visible(timeout=timeout or self.timeout)

    def expect_element_to_contain_text(
        self, selector: str, text: str, timeout: int | None = None
    ) -> None:
        """Expect an element to contain specific text.

        Args:
            selector: CSS selector for the element
            text: Text to expect
            timeout: Timeout in milliseconds
        """
        element = self.page.locator(selector)
        expect(element).to_contain_text(text, timeout=timeout or self.timeout)

    def scroll_to_element(self, selector: str) -> None:
        """Scroll to an element.

        Args:
            selector: CSS selector for the element
        """
        element = self.page.locator(selector)
        element.scroll_into_view_if_needed()

    def handle_dialog(self, action: str = "accept", text: str = None) -> None:
        """Handle JavaScript dialogs (alerts, confirms, prompts).

        Args:
            action: "accept" or "dismiss"
            text: Text to enter for prompts
        """

        def dialog_handler(dialog):
            if action == "accept":
                if text:
                    dialog.accept(text)
                else:
                    dialog.accept()
            else:
                dialog.dismiss()

        self.page.on("dialog", dialog_handler)
