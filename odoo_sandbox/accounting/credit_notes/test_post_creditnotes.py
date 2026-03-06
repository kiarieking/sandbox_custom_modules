import time
from selenium.webdriver import Keys
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

def test_make_payment_creditnote(driver,login,accounting_icon):
    login(EMAIL,PASSWORD)
    accounting_icon()
    status = "Posted"
    credit_note_no = "RINV/2025/0006"
    doc_type = "Credit Notes"
    grp_opn.group_by(driver,doc_type)
    open_specific_credit_note(driver,status,credit_note_no)
    make_payment(driver)
    time.sleep(5)

def test_send_print_invoice(driver,login,accounting_icon):
    login(EMAIL,PASSWORD)
    accounting_icon()
    status = "Posted"
    doc_type = "Credit Notes"
    grp_opn.group_by(driver,doc_type)
    grp_opn.open_doc(driver,status)
    send_print_creditnote(driver)

@pytest.mark.order(27)
def test_reset_creditnote(driver,login,accounting_icon):
    login(EMAIL,PASSWORD)
    accounting_icon()
    status = "Posted"
    doc_type = "Credit Notes"
    grp_opn.group_by(driver,doc_type)
    grp_opn.open_doc(driver,status)
    reset_creditnote(driver)

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
    credit_note = wait.until(
        EC.visibility_of_element_located((By.XPATH, first_credit_note_xpath))
    )
    credit_note.click()

def open_specific_credit_note(driver,status,invoice_no):
    status_xpath = f"//th[@class='o_group_name' and contains(normalize-space(), '{status}')]"
    invoice_grp = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH,status_xpath)))
    invoice_grp.click()
    invoice_xpath = f"//td[@name='name' and normalize-space()='{invoice_no}']"
    invoice = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH,invoice_xpath)))
    invoice.click()

def make_payment(driver):
    register_payment_btn = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.NAME,"action_register_payment")))
    register_payment_btn.click()
    create_payment_btn = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.NAME,"action_create_payments")))
    create_payment_btn.click()
    time.sleep(3)

def send_print_creditnote(driver):
    send_print_btn = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.NAME,"action_invoice_sent")))
    send_print_btn.click()
    send_invoice_txt = WebDriverWait(driver,30).until(EC.presence_of_element_located((By.XPATH,"//h4[normalize-space()='Send Invoice']")))
    assert send_invoice_txt.is_displayed

def reset_creditnote(driver):
    cancel_btn = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH,"//button[.//span[normalize-space()='Reset to Draft']]")))
    cancel_btn.click()
    time.sleep(3)
    status = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, "//button[@data-value='draft']")))
    title = status.get_attribute("title")
    assert title == "Current state"