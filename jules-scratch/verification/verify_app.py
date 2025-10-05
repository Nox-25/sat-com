from playwright.sync_api import sync_playwright, expect

def verify_streamlit_app():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 2400})

        try:
            # 1. Navigate to the Streamlit app
            page.goto("http://localhost:8501", timeout=60000)

            # 2. Wait for the app to be ready
            expect(page.get_by_text("Weather Prediction System")).to_be_visible(timeout=30000)

            # 3. Find and click the "Get Weather" button
            predict_button = page.get_by_role("button", name="Get Weather")
            expect(predict_button).to_be_enabled()
            predict_button.click()

            # 4. Wait for the folium map to render
            map_frame = page.frame_locator("iframe[title='streamlit-folium.st_folium']")
            expect(map_frame.locator(".folium-tile-container")).to_be_visible(timeout=45000)

            # 5. Take a screenshot of the entire page
            page.screenshot(path="jules-scratch/verification/final_verification.png", full_page=True)
            print("Screenshot saved to jules-scratch/verification/final_verification.png")

        except Exception as e:
            print(f"An error occurred during verification: {e}")
            page.screenshot(path="jules-scratch/verification/error.png")
            print("Error screenshot saved to jules-scratch/verification/error.png")
        finally:
            browser.close()

if __name__ == "__main__":
    verify_streamlit_app()