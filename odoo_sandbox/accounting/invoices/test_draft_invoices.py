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

@pytest.mark.order(18)
def test_confirm_invoice(driver,login,accounting_icon):
    login(EMAIL,PASSWORD)
    accounting_icon()
    # group_invoices(driver)
    status = "Draft"
    invoice_no = "INV/2023/0844"
    doc_type = "Invoices"
    grp_opn.group_by(driver,doc_type)
    grp_opn.open_doc(driver,status)
    # open_invoices(driver,status) 
    confirm_invoice(driver)
    time.sleep(3)

@pytest.mark.order(19)
def test_preview_invoice(driver,login,accounting_icon):
    login(EMAIL,PASSWORD)
    accounting_icon()
    status = "Draft"
    doc_type = "Invoices"
    grp_opn.group_by(driver,doc_type)
    grp_opn.open_doc(driver,status)
    preview_invoice(driver)
    time.sleep(3)

@pytest.mark.order(20)
def test_cancel_invoice(driver,login,accounting_icon):
    login(EMAIL,PASSWORD)
    accounting_icon()
    status = "Draft"
    invoice_no = "INV/2023/0844"
    doc_type = "Invoices"
    grp_opn.group_by(driver,doc_type)
    grp_opn.open_doc(driver,status)
    cancel_invoice(driver)
    time.sleep(3)


def group_invoices(driver):
    customers_btn = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH, "//button[.//span[normalize-space()='Customers']]")))
    customers_btn.click()
    invoices = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH,"//a[normalize-space()='Invoices']")))
    invoices.click()
    WebDriverWait(driver,15).until(
        EC.visibility_of_element_located(
            (By.XPATH, "//li[contains(@class,'breadcrumb-item') and contains(@class,'active')]//span[normalize-space()='Invoices']")
        )
    )

    group_by = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH,"//span[@class='o_dropdown_title' and normalize-space()='Group By']")))
    group_by.click()
    status = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH, "//span[@role='menuitemcheckbox' and normalize-space()='Status']")))
    status.click()

def open_invoices(driver,status):
    print(">>> USING NEW open_invoices <<<")
    status_xpath = f"//th[@class='o_group_name' and contains(normalize-space(), '{status}')]"
    invoice_grp = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH,status_xpath)))
    invoice_grp.click()
    wait = WebDriverWait(driver, 20)
    wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//tbody//tr[contains(@class,'o_data_row')]")
        )
    )

    first_invoice_xpath = (
        "(//tbody//tr[contains(@class,'o_data_row')]"
        "//td[@name='name'])[1]"
    )

    # WAIT: element is visible (NOT clickable)
    invoice = wait.until(
        EC.visibility_of_element_located((By.XPATH, first_invoice_xpath))
    )
    invoice.click()

    # Scroll into view (critical for Odoo)
    #driver.execute_script(
        # "arguments[0].scrollIntoView({block:'center'});", invoice
    # )

    # Click with JS fallback
    # try:
    #     invoice.click()
    # except Exception:
    #     driver.execute_script("arguments[0].click();", invoice)

def confirm_invoice(driver):
    confirm_btn = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH,"//button[.//span[normalize-space()='Confirm']]")))
    confirm_btn.click()
    time.sleep(2)
    status = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, "//button[contains(@class,'o_arrow_button') and @data-value='posted']")))
    title = status.get_attribute("title")
    assert title == "Current state"
    time.sleep(3)

def preview_invoice(driver):
    preview_btn = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH,"//button[@name='preview_invoice' and @title='Preview invoice']")))
    preview_btn.click()
    WebDriverWait(driver,10).until(
    EC.presence_of_all_elements_located((
        By.XPATH, 
        "//a[contains(@class,'o_download_btn')] | //a[contains(@class,'o_portal_invoice_print')] | //div[contains(.,'This is a preview of the customer portal')]"
    ))
    )

def cancel_invoice(driver):
    cancel_btn = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH,"//button[@name='button_cancel' and .//span[normalize-space()='Cancel']]")))
    cancel_btn.click()
    time.sleep(2)
    status = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, "//button[contains(@class,'o_arrow_button') and @data-value='cancel']")))
    title = status.get_attribute("title")
    assert title == "Current state"
    
