"""
Automation Flow C — Form Logic Validation (Flow C)

Simple, robust Selenium script in the same style as Flow B (positive flow).

Checks:
  1. Change Country -> States dropdown updates
  2. Change State -> Cities dropdown updates
  3. Password strength meter updates (weak -> strong)
  4. Wrong Confirm Password -> inline error appears
  5. Submit remains disabled until all fields valid, enabled when fixed

Saves screenshots for each step into Automation/automation_output/.
"""

import os
import time
from datetime import datetime
from typing import List

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    WebDriverException,
    ElementNotInteractableException,
    StaleElementReferenceException,
)
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

OUT = os.path.join(os.path.dirname(__file__), "automation_output")
os.makedirs(OUT, exist_ok=True)


def ts() -> str:
    """Return a timestamp string used for naming screenshots and HTML logs."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def save_screenshot(driver, name: str) -> str:
    """Capture a screenshot with a timestamp and save it inside automation_output/."""

    path = os.path.join(OUT, f"{name}_{ts()}.png")
    try:
        driver.save_screenshot(path)
    except (WebDriverException, OSError) as e:
        print("Screenshot save failed:", e)
    return path


def option_values(driver, selector: str) -> List[str]:
    """Return list of option values (or text if value empty)."""
    try:
        opts = driver.find_elements(By.CSS_SELECTOR, selector + " option")
        return [o.get_attribute("value") or o.text for o in opts]
    except (WebDriverException, StaleElementReferenceException):
        # Known selenium-related errors: return empty list but allow other exceptions to surface.
        return []


def wait_for_options_change(driver, selector: str, old: List[str], timeout: int = 4) -> bool:
    """Wait until the list of option values for selector differs from old."""
    try:
        wait = WebDriverWait(driver, timeout)
        return wait.until(lambda d: option_values(d, selector) != old)
    except TimeoutException:
        return False


def find_pwd_strength_text(driver) -> str:
    """Try common places for a textual password strength indicator."""
    candidates = [
        (By.CSS_SELECTOR, ".pwdText"),
        (By.ID, "pwdText"),
        (By.CSS_SELECTOR, ".pwd-text"),
        (By.CSS_SELECTOR, "#pwdMeterBar"),
    ]
    for by, sel in candidates:
        try:
            el = driver.find_element(by, sel)
            txt = (el.text or el.get_attribute("textContent") or "").strip()
            if txt:
                return txt
        except (NoSuchElementException, WebDriverException, StaleElementReferenceException):
            continue
    # fallback: attempt to read width style of #pwdMeterBar
    try:
        width = driver.execute_script(
            "const b=document.querySelector('#pwdMeterBar');"
            "if(!b) return ''; return b.style.width || window.getComputedStyle(b).width || '';"
        )
        return str(width)
    except WebDriverException:
        return ""


def find_confirm_error(driver) -> str:
    """Try common locators for an inline confirm-password error and return its text."""
    confirm_error_xpath = (
        "//*[contains(@id,'confirm') and "
        "contains(translate(@class,'ERROR','error'),'err')]"
    )

    locators = [
        (By.ID, "confirmPasswordErr"),
        (By.CSS_SELECTOR, "#confirmPassword + .error"),
        (By.CSS_SELECTOR, ".confirm-password-error"),
        (By.CSS_SELECTOR, ".error"),
        (By.XPATH, confirm_error_xpath),
    ]

    for by, sel in locators:
        try:
            el = driver.find_element(by, sel)
            txt = (el.text or el.get_attribute("textContent") or "").strip()
            if txt:
                return txt
        except (NoSuchElementException, WebDriverException, StaleElementReferenceException):
            continue
    return ""


def main() -> None:
    """Run Automation Flow C:
    - Validate Country → State update
    - Validate State → City update
    - Validate password strength
    - Validate wrong Confirm Password error
    - Validate submit button enabling logic
    """
    opts = Options()
    opts.add_argument("--window-size=1200,900")
    # opts.add_argument("--headless=new")  # keep visible during debugging

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=opts)

    summary = {
        "states_updated": False,
        "cities_updated": False,
        "pwd_meter_changed": False,
        "confirm_error_shown": False,
        "submit_disabled_until_valid": False,
    }

    try:
        index_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "index.html"))
        driver.get("file://" + index_path)
        time.sleep(0.6)
        print("URL:", driver.current_url)
        print("Title:", driver.title)

        country_sel = "#country"
        state_sel = "#state"
        city_sel = "#city"

        # baseline values
        init_states = option_values(driver, state_sel)
        init_cities = option_values(driver, city_sel)
        print("Initial states count:", len(init_states))
        print("Initial cities count:", len(init_cities))

        try:
            if driver.find_elements(By.CSS_SELECTOR, f"{country_sel} option[value='IN']"):
                driver.find_element(By.CSS_SELECTOR, f"{country_sel} option[value='IN']").click()
            else:
                opts_list = driver.find_elements(By.CSS_SELECTOR, country_sel + " option")
                if len(opts_list) > 1:
                    opts_list[1].click()
        except (
            NoSuchElementException,
            WebDriverException,
            ElementNotInteractableException,
            StaleElementReferenceException,
        ):
            pass
        time.sleep(0.35)

        states_changed = wait_for_options_change(driver, state_sel, init_states, timeout=5)
        current_states = option_values(driver, state_sel)
        summary["states_updated"] = bool(states_changed and current_states != init_states)
        print("States updated:", summary["states_updated"], " -> sample:", current_states[:6])
        save_screenshot(driver, "step1_country_state")

        # Step 2: change state -> expect cities update
        # choose Telangana if present else second option
        chosen_state = None
        for v in current_states:
            if v and "Telangana" in str(v):
                chosen_state = v
                break
        if not chosen_state:
            opts_list = driver.find_elements(By.CSS_SELECTOR, state_sel + " option")
            if len(opts_list) > 1:
                chosen_state = opts_list[1].get_attribute("value") or opts_list[1].text

        try:
            if chosen_state:
                state_option = f"{state_sel} option[value='{chosen_state}']"
                driver.find_element(By.CSS_SELECTOR, state_option).click()

            else:
                opts_list = driver.find_elements(By.CSS_SELECTOR, state_sel + " option")
                if len(opts_list) > 1:
                    opts_list[1].click()
        except (
            NoSuchElementException,
            WebDriverException,
            ElementNotInteractableException,
            StaleElementReferenceException,
        ):
            pass
        time.sleep(0.25)

        cities_changed = wait_for_options_change(driver, city_sel, init_cities, timeout=5)
        current_cities = option_values(driver, city_sel)
        summary["cities_updated"] = bool(cities_changed and current_cities != init_cities)
        print("Cities updated:", summary["cities_updated"], " -> sample:", current_cities[:6])
        save_screenshot(driver, "step2_state_city")

        # Step 3: password strength check
        try:
            pw_el = driver.find_element(By.ID, "password")
        except NoSuchElementException:
            pw_el = None

        weak_text = ""
        strong_text = ""
        if pw_el:
            pw_el.clear()
            pw_el.send_keys("12345")
            time.sleep(0.45)
            weak_text = find_pwd_strength_text(driver)
            print("Weak indicator:", weak_text)
            save_screenshot(driver, "step3_pwd_weak")

            pw_el.clear()
            pw_el.send_keys("Str0ngP@ssw0rd!")
            time.sleep(0.6)
            strong_text = find_pwd_strength_text(driver)
            print("Strong indicator:", strong_text)
            save_screenshot(driver, "step3_pwd_strong")

            password_meter_changed = (
                weak_text
                and strong_text
                and weak_text != strong_text
            )

            summary["pwd_meter_changed"] = bool(password_meter_changed)


        # Step 4: wrong confirm password -> error should appear
        try:
            cpw_el = driver.find_element(By.ID, "confirmPassword")
            cpw_el.clear()
            cpw_el.send_keys("WrongPassword")
            # blur to trigger validation
            driver.execute_script("arguments[0].blur();", cpw_el)
            time.sleep(0.45)
        except NoSuchElementException:
            pass

        confirm_err = find_confirm_error(driver)
        summary["confirm_error_shown"] = bool(confirm_err)
        print("Confirm password error text:", repr(confirm_err))
        save_screenshot(driver, "step4_confirm_error")

        # Step 5: submit disabled until valid -> fill remaining fields but keep confirm wrong
        try:
            fn = driver.find_element(By.ID, "firstName")
            ln = driver.find_element(By.ID, "lastName")
            em = driver.find_element(By.ID, "email")
            ph = driver.find_element(By.ID, "phone")
            tcb = driver.find_element(By.ID, "terms")
        except NoSuchElementException:
            fn = ln = em = ph = tcb = None

        try:
            if fn:
                fn.clear()
                fn.send_keys("FlowC")

            if ln:
                ln.clear()
                ln.send_keys("Tester")

            if em:
                em.clear()
                em.send_keys("flowc.tester@example.com")

            if ph:
                ph.clear()
                ph.send_keys("+919876543210")

            if tcb and not tcb.is_selected():
                tcb.click()

        except (
            NoSuchElementException,
            WebDriverException,
            ElementNotInteractableException,
            StaleElementReferenceException
        ):
            # Ignore known Selenium-related errors when interacting with the fields.
            pass


        time.sleep(0.4)
        try:
            submit_btn = driver.find_element(By.ID, "submitBtn")
        except NoSuchElementException:
            submit_btn = None

        before_enabled = bool(submit_btn and submit_btn.is_enabled())
        print("Submit enabled with wrong confirm?:", before_enabled)

        # fix confirm to match strong password
        try:
            if cpw_el:
                cpw_el.clear()
                cpw_el.send_keys("Str0ngP@ssw0rd!")
                driver.execute_script("arguments[0].blur();", cpw_el)
        except (
            NoSuchElementException,
            WebDriverException,
            ElementNotInteractableException,
            StaleElementReferenceException,
        ):
            # Ignore known Selenium-related errors when interacting with the confirm field.
            pass

        time.sleep(0.5)
        after_enabled = bool(submit_btn and submit_btn.is_enabled())
        print("Submit enabled after fixing confirm?:", after_enabled)
        summary["submit_disabled_until_valid"] = (not before_enabled) and after_enabled
        save_screenshot(driver, "step5_submit_state")

        # Summary printout
        print("\nFlow C summary:")
        for k, v in summary.items():
            print(f" - {k}: {v}")

        # save page source for evidence
        html_file = os.path.join(OUT, f"page_source_{ts()}.html")
        try:
            with open(html_file, "w", encoding="utf-8") as fh:
                fh.write(driver.page_source)
            print("Saved page source to:", html_file)
        except (OSError, WebDriverException) as e:
            print("Failed to save page source:", e)

    finally:
        time.sleep(0.6)
        driver.quit()


if __name__ == "__main__":
    main()
