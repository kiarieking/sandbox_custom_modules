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


@pytest.mark.order(22)
def test_payment_invoice(driver,login,accounting_icon):
    login(EMAIL,PASSWORD)
    accounting_icon()
    doc_type = "Invoices"
    status = "Posted"
    invoice_no = "INV/2025/0418"
    grp_opn.group_by(driver,doc_type)
    open_specific_invoice(driver,status,invoice_no)
    make_payment(driver)

@pytest.mark.order(23)
def test_add_credit_note(driver,login,accounting_icon):
    login(EMAIL,PASSWORD)
    accounting_icon()
    doc_type = "Invoices"
    status = "Posted"
    grp_opn.group_by(driver,doc_type)
    grp_opn.open_doc(driver,status)
    add_creditnote(driver)

@pytest.mark.order(24)
def test_send_print_invoice(driver,login,accounting_icon):
    login(EMAIL,PASSWORD)
    accounting_icon()
    status = "Posted"
    doc_type = "Invoices"
    grp_opn.group_by(driver,doc_type)
    grp_opn.open_doc(driver,status)
    send_print_invoice(driver)


def open_specific_invoice(driver,status,invoice_no):
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

def add_creditnote(driver):
    add_creditnote_btn = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.NAME,"action_reverse")))
    add_creditnote_btn.click()
    reverse_btn = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.NAME,"reverse_moves")))
    reverse_btn.click()
    time.sleep(3)

def send_print_invoice(driver):
    send_print_btn = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.NAME,"action_invoice_sent")))
    send_print_btn.click()
    send_invoice_txt = WebDriverWait(driver,30).until(EC.presence_of_element_located((By.XPATH,"//h4[normalize-space()='Send Invoice']")))
    assert send_invoice_txt.is_displayed