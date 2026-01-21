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

@pytest.mark.order(21)
def test_edit_invoice(driver,login,accounting_icon):
    login(EMAIL,PASSWORD)
    accounting_icon()
    group_invoices(driver)
    status = "Draft"
    open_invoices(driver,status)
    edit_invoice_details(driver) 
    # edit_invoice_line(driver)
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

def edit_invoice_details(driver):
    edit_btn = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH,"//button[contains(@class,'o_form_button_edit') and @title='Edit record']")))
    edit_btn.click()
    # # invoice_no = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH,"//input[@name='name' and @placeholder='JRNL/2016/00001']")))
    # # invoice_no.click()
    # invoice_no.clear()
    # invoice_no.send_keys("Invoices/INV/2025/0707")
    customer = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH,"//input[@type='text' and contains(@class,'ui-autocomplete-input')]")))
    customer.click()
    select_customer = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH,"//a[contains(@class,'ui-menu-item-wrapper') and normalize-space()='IN MOTION REGIONAL LOGISTICS LIMITED']")))
    select_customer.click()
    payment_terms = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH,"//input[@placeholder='T﻿e﻿r﻿m﻿s' and contains(@class,'ui-autocomplete-input')]")))
    payment_terms.click()
    select_terms = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH,"//a[normalize-space()='30 Days']")))
    select_terms.click()
    payment_reference = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH,"//input[contains(@class,'o_field_char') and @name='payment_reference']")))
    payment_reference.click()
    payment_reference.clear()
    payment_reference.send_keys("INV/2023/0844")
    save_btn = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH,"//span[normalize-space()='Save']")))
    save_btn.click()

def edit_invoice_line(driver):
    edit_btn = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH,"//button[contains(@class,'o_form_button_edit') and @title='Edit record']")))
    edit_btn.click()

    wait = WebDriverWait(driver, 10)
    product_cell_xpath = (
        "(//tbody[contains(@class,'ui-sortable')]"
        "//tr[contains(@class,'o_data_row')])[1]"
        "//td[@name='product_id']"
    )

    cell = wait.until(EC.element_to_be_clickable((By.XPATH, product_cell_xpath)))

    # Activate editor
    ActionChains(driver).double_click(cell).perform()
    time.sleep(3)
    ActionChains(driver)\
        .send_keys(Keys.CONTROL, "a")\
        .send_keys("MIWANI")\
        .send_keys(Keys.ENTER)\
        .perform()

    time.sleep(3)

    save_btn = wait.until(EC.element_to_be_clickable((
    By.XPATH, "//button[contains(@class,'o_form_button_save')]"
)))
    save_btn.click()