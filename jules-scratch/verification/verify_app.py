from playwright.sync_api import sync_playwright, expect

def verify_streamlit_app():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 1920})

        try:
            # 1. Navigate to the Streamlit app
            page.goto("http://localhost:8501", timeout=60000)

            # 2. Wait for the app to be ready
            # We'll wait for the main title to be visible
            expect(page.get_by_text("Weather Prediction System")).to_be_visible(timeout=30000)

            # 3. Find and click the "Get Weather and Predict" button
            # The default city is "London", so we don't need to enter it.
            predict_button = page.get_by_role("button", name="Get Weather and Predict")
            expect(predict_button).to_be_enabled()
            predict_button.click()

            # 4. Wait for the results to appear
            # We'll wait for the "Current Weather Conditions" subheader to show up after the button click.
            expect(page.get_by_text("Current Weather Conditions")).to_be_visible(timeout=30000)

            # 5. Take a screenshot of the entire page
            page.screenshot(path="jules-scratch/verification/verification.png", full_page=True)
            print("Screenshot saved to jules-scratch/verification/verification.png")

        except Exception as e:
            print(f"An error occurred during verification: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    verify_streamlit_app()