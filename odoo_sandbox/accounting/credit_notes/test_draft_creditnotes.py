import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from accounting.Group_Open_doc import Group_Open_doc
import pytest
from dotenv import load_dotenv
import os

load_dotenv()
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

grp_opn = Group_Open_doc()

@pytest.mark.order(25)
def test_confirm_creditnote(driver,login,accounting_icon):
    login(EMAIL,PASSWORD)
    accounting_icon()
    status = "Draft"
    doc_type = "Credit Notes"
    grp_opn.group_by(driver,doc_type)
    grp_opn.open_doc(driver,status)
    confirm_creditnote(driver)

@pytest.mark.order(26)
def test_cancel_creditnote(driver,login,accounting_icon):
    login(EMAIL,PASSWORD)
    accounting_icon()
    status = "Draft"
    doc_type = "Credit Notes"
    grp_opn.group_by(driver,doc_type)
    grp_opn.open_doc(driver,status)
    cancel_creditnote(driver)

@pytest.mark.order(26)
def test_preview_creditnote(driver,login,accounting_icon):
    login(EMAIL,PASSWORD)
    accounting_icon()
    status = "Draft"
    doc_type = "Credit Notes"
    grp_opn.group_by(driver,doc_type)
    grp_opn.open_doc(driver,status)
    preview_creditnote(driver)
    
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
