import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pytest
from dotenv import load_dotenv
import os

load_dotenv()
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

@pytest.mark.order(25)
def test_confirm_creditnote(driver,login,accounting_icon):
    login(EMAIL,PASSWORD)
    accounting_icon()
    group_creditnote(driver)
    status = "Draft"
    open_creditnote(driver,status)
    confirm_creditnote(driver)

@pytest.mark.order(26)
def test_cancel_creditnote(driver,login,accounting_icon):
    login(EMAIL,PASSWORD)
    accounting_icon()
    group_creditnote(driver)
    status = "Draft"
    open_creditnote(driver,status)
    cancel_creditnote(driver)

@pytest.mark.order(27)
def test_reset_creditnote(driver,login,accounting_icon):
    login(EMAIL,PASSWORD)
    accounting_icon()
    group_creditnote(driver)
    status = "Cancelled"
    open_creditnote(driver,status)
    reset_creditnote(driver)

@pytest.mark.order(26)
def test_preview_creditnote(driver,login,accounting_icon):
    login(EMAIL,PASSWORD)
    accounting_icon()
    group_creditnote(driver)
    status = "Draft"
    open_creditnote(driver,status)
    preview_creditnote(driver)

def group_creditnote(driver):
    customers_btn = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH, "//button[.//span[normalize-space()='Customers']]")))
    customers_btn.click()
    credit_note = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH,"//a[normalize-space()='Credit Notes']")))
    credit_note.click()
    WebDriverWait(driver,15).until(
        EC.visibility_of_element_located(
            (By.XPATH, "//li[contains(@class,'breadcrumb-item') and contains(@class,'active')]//span[normalize-space()='Credit Notes']")
        )
    )

    group_by = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH,"//span[@class='o_dropdown_title' and normalize-space()='Group By']")))
    group_by.click()
    status = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH, "//span[@role='menuitemcheckbox' and normalize-space()='Status']")))
    status.click()

def open_creditnote(driver,status):
    status_xpath = f"//th[@class='o_group_name' and contains(normalize-space(), '{status}')]"
    credit_note_grp = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH,status_xpath)))
    credit_note_grp.click()
    wait = WebDriverWait(driver, 20)
    wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//tbody//tr[contains(@class,'o_data_row')]")
        )
    )

    first_credit_note_xpath = (
        "(//tbody//tr[contains(@class,'o_data_row')]"
        "//td[@name='name'])[1]"
    )

    # WAIT: element is visibfrom selenium.webdriver.common.keys import Keysle (NOT clickable)
    invoice = wait.until(
        EC.visibility_of_element_located((By.XPATH, first_credit_note_xpath))
    )
    invoice.click()
    

def confirm_creditnote(driver):
    confirm_btn = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH,"//button[.//span[normalize-space()='Confirm']]")))
    confirm_btn.click()
    time.sleep(3)
    status = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, "//button[@data-value='posted']")))
    title = status.get_attribute("title")
    assert title == "Current state"

def cancel_creditnote(driver):
    cancel_btn = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH,"//button[.//span[normalize-space()='Cancel']]")))
    cancel_btn.click()
    time.sleep(3)
    status = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, "//button[@data-value='cancel']")))
    title = status.get_attribute("title")
    assert title == "Current state"

def reset_creditnote(driver):
    cancel_btn = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH,"//button[.//span[normalize-space()='Reset to Draft']]")))
    cancel_btn.click()
    time.sleep(3)
    status = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, "//button[@data-value='draft']")))
    title = status.get_attribute("title")
    assert title == "Current state"

def preview_creditnote(driver):
    preview_btn = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH,"//button[@name='preview_invoice' and @title='Preview invoice']")))
    preview_btn.click()
    WebDriverWait(driver,10).until(
    EC.presence_of_all_elements_located((
        By.XPATH, 
        "//a[contains(@class,'o_download_btn')] | //a[contains(@class,'o_portal_invoice_print')] | //div[contains(.,'This is a preview of the customer portal')]"
    ))
    )
