"""Page object for the main Code2MARKDOWN application page."""

from playwright.sync_api import Locator, Page


class MainPage:
    """Page object for the main application page."""

    def __init__(self, page: Page):
        """Initialize the main page object."""
        self.page = page
        self.url = "http://localhost:8501"

    def navigate(self) -> None:
        """Navigate to the main page."""
        self.page.goto(self.url)
        self.page.wait_for_load_state("networkidle")

    def is_loaded(self) -> bool:
        """Check if the main page is loaded."""
        try:
            # Look for Streamlit-specific elements
            self.page.wait_for_selector("[data-testid='stApp']", timeout=5000)
            return True
        except Exception:
            return False

    def get_title(self) -> str:
        """Get the page title."""
        return self.page.title()

    def get_header_text(self) -> str:
        """Get the main header text."""
        header = self.page.locator("h1").first
        return header.text_content() if header else ""

    def has_file_uploader(self) -> bool:
        """Check if file uploader is present."""
        try:
            uploader = self.page.locator("[data-testid='stFileUploader']")
            return uploader.is_visible()
        except Exception:
            return False

    def upload_file(self, file_path: str) -> None:
        """Upload a file using the file uploader."""
        uploader = self.page.locator("[data-testid='stFileUploader'] input[type='file']")
        uploader.set_input_files(file_path)
        # Wait for upload to complete
        self.page.wait_for_timeout(2000)

    def get_output_area(self) -> Locator:
        """Get the output text area."""
        return self.page.locator("[data-testid='stTextArea'] textarea")

    def get_generate_button(self) -> Locator:
        """Get the generate button."""
        return self.page.locator("button").filter(has_text="Generate")

    def click_generate(self) -> None:
        """Click the generate button."""
        button = self.get_generate_button()
        button.click()
        # Wait for generation to complete
        self.page.wait_for_timeout(3000)

    def get_generated_content(self) -> str:
        """Get the generated markdown content."""
        output_area = self.get_output_area()
        return output_area.input_value() if output_area else ""
