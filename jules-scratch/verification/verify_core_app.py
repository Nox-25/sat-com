from playwright.sync_api import sync_playwright, expect

def verify_core_app():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 1800})

        try:
            # 1. Navigate to the Streamlit app
            page.goto("http://localhost:8501", timeout=60000)

            # 2. Wait for the app to be ready
            expect(page.get_by_text("Weather Prediction System")).to_be_visible(timeout=30000)

            # 3. Find and click the "Get Weather" button
            predict_button = page.get_by_role("button", name="Get Weather")
            expect(predict_button).to_be_enabled()
            predict_button.click()

            # 4. Wait for the final section to appear (Prediction Summary)
            expect(page.get_by_text("Prediction Summary")).to_be_visible(timeout=60000)

            # 5. Take a screenshot
            page.screenshot(path="jules-scratch/verification/core_app_stable.png", full_page=True)
            print("Screenshot of core app saved.")

        except Exception as e:
            print(f"An error occurred during core app verification: {e}")
            page.screenshot(path="jules-scratch/verification/core_app_error.png")
            print("Error screenshot saved.")
        finally:
            browser.close()

if __name__ == "__main__":
    verify_core_app()