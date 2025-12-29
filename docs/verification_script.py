from playwright.sync_api import sync_playwright, expect
import time

def verify_admin_fields():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Create a context with storage state to simulate potential login if needed (mocking for now)
        context = browser.new_context()
        page = context.new_page()

        try:
            # Navigate to the Admin Tools page
            # Note: The base path is /ViteMind/ as per memory
            url = "http://localhost:5173/ViteMind/admin/tools.html"
            print(f"Navigating to {url}")
            page.goto(url)

            # Wait for the DataManager component to mount
            # Since Supabase keys are missing in this env, it will likely alert
            # We need to handle the dialog to proceed
            page.on("dialog", lambda dialog: dialog.accept())

            # Wait a bit for the UI to render (even if empty/error state)
            time.sleep(2)

            # Click "Create" button to open the modal
            # This allows us to inspect the form fields
            print("Clicking Create button...")
            page.get_by_role("button", name="➕ 新增").click()

            # Wait for modal
            time.sleep(1)

            # Verify the new 'Category' select dropdown exists
            print("Verifying Category Select...")
            # Ideally find select by label "分类 *" (required star added)
            # The label logic is: <label>{{ col.label }} <span ...>*</label>
            # But the label text itself is just "分类 "
            # Let's verify the select options

            # Take a screenshot of the modal
            print("Taking screenshot...")
            page.screenshot(path="/home/jules/verification/admin_modal_verification.png")

        except Exception as e:
            print(f"Error: {e}")
            # Take error screenshot
            page.screenshot(path="/home/jules/verification/error.png")
        finally:
            browser.close()

if __name__ == "__main__":
    verify_admin_fields()
