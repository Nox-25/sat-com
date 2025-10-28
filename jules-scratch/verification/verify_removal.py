from playwright.sync_api import Page, expect

def test_verify_removal(page: Page):
    """
    This test verifies that the application operates correctly without the map feature.
    """
    # 1. Arrange: Go to the Streamlit application.
    page.goto("http://localhost:8501")

    # 2. Act: Enter a city name and click the "Get Weather" button.
    page.get_by_label("Enter a city name:").fill("London")
    page.get_by_role("button", name="Get Weather").click()

    # Wait for the visualizations to be displayed.
    expect(page.get_by_text("Visualizations")).to_be_visible(timeout=30000)

    # 3. Screenshot: Capture the final result for visual verification.
    page.screenshot(path="jules-scratch/verification/verify_removal.png")
