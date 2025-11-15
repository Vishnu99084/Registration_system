"""
Automation Script: Positive Test Case for the Registration Form (Flow B).

- Fills required fields with valid data
- Ensures Password & Confirm Password match
- Ensures Terms & Conditions checked
- Submits the form
- Validates:
    · Success message appears (captures success-state screenshot)
    · Form fields reset (verifies and captures form-reset screenshot)
- Saves timestamped screenshots and page source into automation_output/
"""

import os
import time
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


OUT_DIR = os.path.join(os.path.dirname(__file__), "automation_output")
os.makedirs(OUT_DIR, exist_ok=True)


def is_input_cleared(el) -> bool:
    """Return True if an input/textarea/select is in cleared/default state."""
    try:
        tag = el.tag_name.lower()
        if tag in ("input", "textarea"):
            return (el.get_attribute("value") or "").strip() == ""
        if tag == "select":
            return (el.get_attribute("value") or "") == ""
        return False
    except (AttributeError, WebDriverException):
        return False


def capture_element_screenshot(driver, locator, path, timeout=5):
    """
    Wait until element located by `locator` (tuple) is visible, then screenshot it.
    Returns (True, text) on success else (False, "").
    """
    try:
        wait = WebDriverWait(driver, timeout)
        el = wait.until(EC.visibility_of_element_located(locator))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
        time.sleep(0.12)
        el.screenshot(path)
        text = (el.text or el.get_attribute("textContent") or "").strip()
        return True, text
    except (NoSuchElementException, TimeoutException, WebDriverException):
        return False, ""


def save_fullpage_screenshot(driver, path):
    """Attempt to save a reasonably large viewport screenshot as a fallback."""
    try:
        # try to expand viewport to full page height (may fail on some drivers)
        width = (
            "return Math.max("
            "document.documentElement.scrollWidth, "
            "document.body.scrollWidth, "
            "1024);"
        )
        height = (
            "return Math.max("
            "document.documentElement.scrollHeight, "
            "document.body.scrollHeight, "
            "800);"
        )
        # clamp to sensible limits
        width = min(int(width), 3840)
        height = min(int(height), 5000)
        try:
            driver.set_window_size(width, height)
            time.sleep(0.12)
        except WebDriverException:
            # ignore if driver can't resize
            pass
        driver.save_screenshot(path)
        return True
    except WebDriverException:
        return False


def main() -> None:
    """Execute the Positive Test Flow:
    - Fill the form with valid data
    - Submit the form
    - Validate success message
    - Validate form reset
    - Capture screenshots and page source
    """
    opts = Options()
    opts.add_argument("--window-size=1200,900")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=opts)

    try:
        index_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "index.html"))
        driver.get("file://" + index_path)
        time.sleep(0.6)

        print("URL:", driver.current_url)
        print("Title:", driver.title)

        # ---------- Fill the form with valid data ----------
        driver.find_element(By.ID, "firstName").clear()
        driver.find_element(By.ID, "firstName").send_keys("Positive")

        driver.find_element(By.ID, "lastName").clear()
        driver.find_element(By.ID, "lastName").send_keys("User")

        driver.find_element(By.ID, "email").clear()
        driver.find_element(By.ID, "email").send_keys("positive.user@example.com")

        # Country -> State -> City (values should match your index.html options)
        driver.find_element(By.CSS_SELECTOR, "#country option[value='IN']").click()
        time.sleep(0.25)
        driver.find_element(By.CSS_SELECTOR, "#state option[value='Telangana']").click()
        time.sleep(0.15)
        driver.find_element(By.CSS_SELECTOR, "#city option[value='Hyderabad']").click()

        driver.find_element(By.ID, "phone").clear()
        driver.find_element(By.ID, "phone").send_keys("+919876543210")

        # choose gender (radio)
        try:
            driver.find_element(By.ID, "genderMale").click()
        except NoSuchElementException:
            # fallback to first radio in gender group
            try:
                radios = driver.find_elements(By.CSS_SELECTOR, "input[type='radio'][name='gender']")
                if radios:
                    radios[0].click()
            except (NoSuchElementException, WebDriverException):
                pass

        # Passwords (must match)
        password_value = "Str0ngP@ssw0rd"
        pw_el = driver.find_element(By.ID, "password")
        cpw_el = driver.find_element(By.ID, "confirmPassword")
        pw_el.clear()
        cpw_el.clear()
        pw_el.send_keys(password_value)
        cpw_el.send_keys(password_value)

        # Ensure Terms & Conditions checked
        terms_el = driver.find_element(By.ID, "terms")
        if not terms_el.is_selected():
            terms_el.click()

        # allow client-side validation logic to run
        time.sleep(0.4)

        # ---------- Submit ----------
        submit_btn = driver.find_element(By.ID, "submitBtn")
        print("Submit enabled:", submit_btn.is_enabled())
        if not submit_btn.is_enabled():
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            debug_path = os.path.join(OUT_DIR, f"submit-disabled-debug_{ts}.png")
            save_fullpage_screenshot(driver, debug_path)
            print("Submit button disabled unexpectedly. Debug screenshot saved to:", debug_path)
            return

        submit_btn.click()

        # ---------- Capture success alert screenshot (required) ----------
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        success_img = os.path.join(OUT_DIR, f"success-state_{ts}.png")  # required artifact
        form_img = os.path.join(OUT_DIR, f"form-reset_{ts}.png")
        page_html = os.path.join(OUT_DIR, f"page_source_{ts}.html")

        success_ok = False
        success_text = ""

        # Try to capture topAlert element
        captured, text = capture_element_screenshot(
            driver,
            (By.ID, "topAlert"),
            success_img,
            timeout=6
        )

        if captured:
            success_text = text
            success_ok = "registration successful" in (text or "").lower()
            print("Captured topAlert element as success screenshot.")
        else:
            # fallback 1: try formMessage element
            try:
                fm = driver.find_element(By.ID, "formMessage")
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", fm)
                time.sleep(0.12)
                fm.screenshot(success_img)
                success_text = (fm.text or "").strip()
                success_ok = "registration successful" in (success_text or "").lower()
                print("Captured formMessage as fallback success screenshot.")
            except (NoSuchElementException, WebDriverException):
                # final fallback: full page screenshot
                saved = save_fullpage_screenshot(driver, success_img)
                if saved:
                    print("Saved fallback full-page screenshot as success image.")
                else:
                    print("Failed to save any success screenshot.")

        print("Success alert text:", repr(success_text))

        # ---------- Verify form fields reset ----------
        time.sleep(0.3)  # wait for potential UI reset
        checks = {
            "firstName": driver.find_element(By.ID, "firstName"),
            "lastName": driver.find_element(By.ID, "lastName"),
            "email": driver.find_element(By.ID, "email"),
            "phone": driver.find_element(By.ID, "phone"),
            "password": driver.find_element(By.ID, "password"),
            "confirmPassword": driver.find_element(By.ID, "confirmPassword"),
            "terms": driver.find_element(By.ID, "terms"),
            "country": driver.find_element(By.ID, "country"),
            "state": driver.find_element(By.ID, "state"),
            "city": driver.find_element(By.ID, "city"),
        }

        reset_ok = True
        reset_issues = []

        for key in ("firstName", "lastName", "email", "phone", "password", "confirmPassword"):
            el = checks[key]
            val = (el.get_attribute("value") or "").strip()
            if val:
                reset_ok = False
                reset_issues.append(f"{key} not reset (value='{val}')")

        if checks["terms"].is_selected():
            reset_ok = False
            reset_issues.append("terms checkbox still selected")

        for sel in ("country", "state", "city"):
            sel_val = (checks[sel].get_attribute("value") or "")
            if sel_val:
                reset_ok = False
                reset_issues.append(f"{sel} not reset (value='{sel_val}')")

        if reset_ok:
            print("Form reset validation: PASS")
        else:
            print("Form reset validation: FAIL")
            for it in reset_issues:
                print(" -", it)

        # ---------- Save form screenshot (proof of reset) ----------
        try:
            form_elem = None
            try:
                form_elem = driver.find_element(By.CSS_SELECTOR, "form")
            except NoSuchElementException:
                form_elem = driver.find_element(By.CSS_SELECTOR, "body > div")
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", form_elem)
            time.sleep(0.12)
            form_elem.screenshot(form_img)
            print("Saved form screenshot:", form_img)
        except (NoSuchElementException, WebDriverException):
            saved = save_fullpage_screenshot(driver, form_img)
            if saved:
                print("Saved fallback form screenshot:", form_img)
            else:
                print("Failed to save form screenshot.")

        # ---------- Save page source for evidence ----------
        try:
            with open(page_html, "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            print("Page source saved to:", page_html)
        except OSError as e:
            print("Failed to save page source:", e)

        overall_ok = success_ok and reset_ok
        print("Overall Flow B result:", "PASS" if overall_ok else "FAIL")

    finally:
        time.sleep(10)
        driver.quit()


if __name__ == "__main__":
    main()
