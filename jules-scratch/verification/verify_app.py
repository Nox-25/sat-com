from playwright.sync_api import sync_playwright, expect
from datetime import date, timedelta

def verify_streamlit_app():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Use a large viewport to capture the whole page
        page = browser.new_page(viewport={"width": 1280, "height": 1920})

        try:
            # 1. Navigate to the Streamlit app
            page.goto("http://localhost:8501", timeout=90000)

            # 2. Wait for the app to be ready
            expect(page.get_by_text("Weather Prediction System")).to_be_visible(timeout=30000)

            # 3. Find and click the main button
            # The default city and dates are fine for verification.
            predict_button = page.get_by_role("button", name="Get Historical Data and Predict")
            expect(predict_button).to_be_enabled()
            predict_button.click()

            # 4. Wait for the final results to appear
            # The visualization header is the last thing to load.
            # We'll give it a generous timeout to allow for API calls and model training.
            expect(page.get_by_text("Historical Data and Prediction Visualization")).to_be_visible(timeout=90000)

            # 5. Take a screenshot of the entire page
            page.screenshot(path="jules-scratch/verification/verification.png", full_page=True)
            print("Screenshot saved to jules-scratch/verification/verification.png")

        except Exception as e:
            print(f"An error occurred during verification: {e}")
            # Capture a screenshot even on failure to help with debugging
            page.screenshot(path="jules-scratch/verification/error.png")
            print("Error screenshot saved to jules-scratch/verification/error.png")
        finally:
            browser.close()

if __name__ == "__main__":
    verify_streamlit_app()