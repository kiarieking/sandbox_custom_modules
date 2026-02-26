import time
from selenium.webdriver import ActionChains, Keys
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

@pytest.mark.order(21)
def test_edit_invoice(driver,login,accounting_icon):
    login(EMAIL,PASSWORD)
    accounting_icon()
    status = "Draft"
    
    grp_opn.group_by(driver)
    grp_opn.open_doc(driver,status)
    # edit_invoice_line(driver)

    edit_invoice_details(driver)
    time.sleep(3)


def edit_invoice_details(driver):
    edit_btn = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH,"//button[contains(@class,'o_form_button_edit') and @title='Edit record']")))
    edit_btn.click()
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