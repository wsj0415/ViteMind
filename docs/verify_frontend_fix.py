from playwright.sync_api import sync_playwright, expect
import time

def verify_xss_protection():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            # Navigate to the page
            url = "http://localhost:5173/ViteMind/design-resources.html"
            print(f"Navigating to {url}")
            # Wait for hydration
            page.goto(url, timeout=60000)

            # Wait a bit for everything to load
            time.sleep(2)

            # Click "Submit Resource" button (Trigger)
            print("Clicking Trigger button...")
            # Using specific class or text
            page.get_by_text("提交资源").first.click()

            # Wait for modal to appear
            print("Waiting for modal...")
            expect(page.locator(".modal-content")).to_be_visible()

            # Fill in the form with malicious URL
            print("Filling form...")
            page.fill("#resource-title", "XSS Test")
            page.fill("#resource-url", "javascript:alert(1)")
            page.fill("#resource-desc", "Malicious description")

            # Click Submit inside modal
            print("Clicking Submit inside modal...")
            page.locator(".modal-content .submit-btn").click()

            # Verify error message
            # The message should be "无效的资源链接 (必须是 http 或 https)"
            print("Verifying error message...")
            error_msg = page.get_by_text("无效的资源链接 (必须是 http 或 https)")
            expect(error_msg).to_be_visible()

            # Screenshot
            print("Taking screenshot...")
            page.screenshot(path="docs/verification_xss_fix.png")
            print("Screenshot saved to docs/verification_xss_fix.png")

        except Exception as e:
            print(f"Error: {e}")
            page.screenshot(path="docs/verification_error.png")
            raise e
        finally:
            browser.close()

if __name__ == "__main__":
    verify_xss_protection()
