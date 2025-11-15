"""
Automation Script: Negative Test Case for the Registration Form.

This script fills the registration form but intentionally leaves the Last Name
empty to validate client-side error handling. Uses selenium + webdriver-manager.
Saves a screenshot and page source to help debug if the inline error is missing.
"""

import os
import time
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


def main() -> None:
    """Main entry for the negative form test."""
    # Output folder for screenshots/logs (inside Automation/)
    out_dir = os.path.join(os.path.dirname(__file__), "automation_output")
    os.makedirs(out_dir, exist_ok=True)

    # Chrome options
    opts = Options()
    opts.add_argument("--window-size=1200,900")
    # opts.add_argument("--headless=new")  # Uncomment for headless; ensure window-size

    # Use webdriver-manager to automatically download the matching chromedriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=opts)

    try:
        # Construct file:// path to index.html (project root is parent of Automation/)
        index_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "index.html")
        )
        path = "file://" + index_path
        driver.get(path)

        # short wait for page to load
        time.sleep(0.8)
        print("URL:", driver.current_url)
        print("Title:", driver.title)

        # Fill fields (skip last name on purpose)
        driver.find_element(By.ID, "firstName").send_keys("Vishnu")
        driver.find_element(By.ID, "email").send_keys("vishnuthammadaveni@gmail.com")

        # Select Country -> State -> City (India -> Telangana -> Hyderabad)
        country_opt = driver.find_element(
            By.CSS_SELECTOR, "#country option[value='IN']"
        )
        country_opt.click()
        time.sleep(0.35)
        state_opt = driver.find_element(
            By.CSS_SELECTOR, "#state option[value='Telangana']"
        )
        state_opt.click()
        time.sleep(0.2)
        city_opt = driver.find_element(
            By.CSS_SELECTOR, "#city option[value='Hyderabad']"
        )
        city_opt.click()

        # Phone, gender, password, terms
        driver.find_element(By.ID, "phone").send_keys("+919876543210")
        driver.find_element(By.ID, "genderMale").click()
        driver.find_element(By.ID, "password").send_keys("Vishnu@#9908")
        driver.find_element(By.ID, "confirmPassword").send_keys("Vishnu@#9908")
        driver.find_element(By.ID, "terms").click()

        # Attempt to submit
        driver.find_element(By.ID, "submitBtn").click()
        # wait a short moment for inline validation to appear
        time.sleep(0.6)

        # ----- robust element lookup with better error handling -----
        try:
            wait = WebDriverWait(driver, 5)
            last_elem = wait.until(
                EC.presence_of_element_located((By.ID, "lastNameErr"))
            )
            # Prefer visible text, but fall back to textContent if text is empty
            last_name_err = (
                last_elem.text or last_elem.get_attribute("textContent") or ""
            )
            last_name_err = last_name_err.strip()
            if not last_name_err:
                last_name_err = "(lastNameErr present but empty)"
        except TimeoutException:
            last_name_err = "(lastNameErr element not found within 5s)"
        except WebDriverException as wde:
            last_name_err = (
                f"(WebDriverException reading lastNameErr: "
                f"{type(wde).__name__}: {wde})"
            )

        print("LastName error text:", last_name_err)

        # always save a screenshot and page source to help debug
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_file = f"error-state_{ts}.png"
        html_file = f"page_source_{ts}.html"
        screenshot_path = os.path.join(out_dir, screenshot_file)
        html_path = os.path.join(out_dir, html_file)

        # === Better screenshot: capture the entire form element (recommended) ===
        try:
            # try to capture the form or main container (adjust selector if needed)
            try:
                form_elem = driver.find_element(By.CSS_SELECTOR, "form")
            except NoSuchElementException:
                # fallback: try a large wrapper / first div under body
                form_elem = driver.find_element(By.CSS_SELECTOR, "body > div")

            # Scroll the element into view and wait briefly for rendering
            driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", form_elem
            )
            time.sleep(0.4)

            # Save element screenshot (guarantees the form content is included)
            form_elem.screenshot(screenshot_path)
            print("Screenshot saved to:", screenshot_path)

        except (NoSuchElementException, WebDriverException) as sce:
            # fallback to full-page viewport screenshot if element screenshot fails
            print("Element screenshot failed:", sce)
            try:
                # try to resize to full page height for a fuller screenshot
                width = driver.execute_script(
                    "return Math.max(document.documentElement.scrollWidth, "
                    "document.body.scrollWidth, 1024);"
                )
                height = driver.execute_script(
                    "return Math.max(document.documentElement.scrollHeight, "
                    "document.body.scrollHeight, 800);"
                )
                width = min(int(width), 3840)
                height = min(int(height), 5000)
                driver.set_window_size(width, height)
                time.sleep(0.4)
            except WebDriverException:
                # ignore resize problems and proceed to save viewport screenshot
                pass

            try:
                driver.save_screenshot(screenshot_path)
                print("Fallback screenshot saved to:", screenshot_path)
            except WebDriverException as e2:
                print("Failed to save screenshot:", e2)

        # Save page source for debugging (always attempt this)
        try:
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            print("Page source saved to:", html_path)
        except OSError as e:
            print("Failed to save page source:", e)

    finally:
        # small delay so you can see browser state (if watching), then quit
        time.sleep(15)
        driver.quit()


if __name__ == "__main__":
    main()
