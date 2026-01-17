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

@pytest.mark.order(22)
def test_payment_invoice(driver,login,accounting_icon):
    login(EMAIL,PASSWORD)
    accounting_icon()
    group_invoices(driver)
    status = "Posted"
    open_invoices(driver,status)
    make_payment(driver)

@pytest.mark.order(23)
def test_add_credit_note(driver,login,accounting_icon):
    login(EMAIL,PASSWORD)
    accounting_icon()
    group_invoices(driver)
    status = "Posted"
    open_invoices(driver,status)
    add_creditnote(driver)

@pytest.mark.order(24)
def test_send_print_invoice(driver,login,accounting_icon):
    login(EMAIL,PASSWORD)
    accounting_icon()
    group_invoices(driver)
    status = "Posted"
    open_invoices(driver,status)
    send_print_invoice(driver)

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

# def open_invoices(driver,status,invoice_no):
#     status_xpath = f"//th[@class='o_group_name' and contains(normalize-space(), '{status}')]"
#     invoice_grp = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH,status_xpath)))
#     invoice_grp.click()
#     invoice_xpath = f"//td[@name='name' and normalize-space()='{invoice_no}']"
#     invoice = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH,invoice_xpath)))
#     invoice.click()

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

def make_payment(driver):
    register_payment_btn = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.NAME,"action_register_payment")))
    register_payment_btn.click()
    create_payment_btn = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.NAME,"action_create_payments")))
    create_payment_btn.click()
    time.sleep(3)

def add_creditnote(driver):
    add_creditnote_btn = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.NAME,"action_reverse")))
    add_creditnote_btn.click()
    refund_btn = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH,"//label[normalize-space()='Full Refund']")))
    refund_btn.click()
    reverse_btn = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.NAME,"reverse_moves")))
    reverse_btn.click()
    time.sleep(3)

def send_print_invoice(driver):
    send_print_btn = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.NAME,"action_invoice_sent")))
    send_print_btn.click()
    send_invoice_txt = WebDriverWait(driver,30).until(EC.presence_of_element_located((By.XPATH,"//h4[normalize-space()='Send Invoice']")))
    assert send_invoice_txt.is_displayed