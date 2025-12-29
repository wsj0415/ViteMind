from playwright.sync_api import sync_playwright, expect

def verify_admin_ui():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            # Visit with correct Base URL
            # The dev server is running at port 3333
            # Base URL is /ViteMind/
            url = "http://localhost:3333/ViteMind/admin/index"
            print(f"Navigating to {url}...")
            page.goto(url)

            # Wait for redirect logic to settle (AdminLayout checks session -> redirects to login)
            page.wait_for_timeout(3000)

            # We expect to be on the login page or see login elements
            # Check for specific text from AdminLogin.vue
            if page.get_by_text("ViteMind Admin").is_visible():
                print("Verified: 'ViteMind Admin' title is visible.")

            if page.get_by_placeholder("admin@example.com").is_visible():
                print("Verified: Email input is visible.")

            page.screenshot(path="/home/jules/verification/admin_login_success.png")
            print("Captured admin_login_success.png")

        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    verify_admin_ui()
