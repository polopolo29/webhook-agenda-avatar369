from playwright.sync_api import sync_playwright
import os

def run_verification():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # Go to the local HTML file
        file_path = os.path.abspath('jules-scratch/verification/index.html')
        page.goto(f'file://{file_path}')

        # Wait for the initial message from the bot
        page.wait_for_selector('.bot-message')

        # Simulate a user sending a message
        page.fill('#chat-input', 'Juan Perez')
        page.click('#chat-send')

        # Wait for the bot's response
        page.wait_for_selector('.bot-message:nth-child(2)')

        # Take a screenshot
        screenshot_path = 'jules-scratch/verification/verification.png'
        page.screenshot(path=screenshot_path)
        print(f"Screenshot saved to {screenshot_path}")

        browser.close()

if __name__ == "__main__":
    run_verification()
