from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from dotenv import load_dotenv
from Group_Open_Order import Group_Open_Order
import os
import time
import pytest

load_dotenv()
EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')

grp_opn = Group_Open_Order()

@pytest.mark.order(7)
def test_confirm_order(driver,login,carrier_icon):
    status = "Quotation"
    carrier_no = "CO13436"
    login(EMAIL,PASSWORD)
    carrier_icon()
    grp_opn.group_vouchers(driver)
    grp_opn.open_voucher(driver,status)
    confirm_order(driver)
    time.sleep(2)

@pytest.mark.order(8)
def test_post_order(driver,login,carrier_icon):
    status = "Order"
    carrier_no = "CO03020"
    login(EMAIL,PASSWORD)
    carrier_icon()
    group_orders(driver)
    open_order(driver,status)
    post_order(driver)
    time.sleep(2)

@pytest.mark.order(9)
def test_cancel_order(driver,login,carrier_icon):
    status = "Posted"
    carrier_no = "CO13433"
    login(EMAIL,PASSWORD) 
    carrier_icon()
    group_orders(driver)
    open_order(driver,status)
    cancel_order(driver)
    time.sleep(2)

@pytest.mark.order(10)
def test_reset_order(driver,login,carrier_icon):
    status = "Cancelled"
    carrier_no = "CO10770"
    login(EMAIL,PASSWORD)
    carrier_icon()
    group_orders(driver)
    open_order(driver,status)
    reset_order(driver)
    time.sleep(2)

def group_orders(driver):
    group_by = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[@class='dropdown-toggle btn btn-light ' and .//span[normalize-space()='Group By']]")))
    group_by.click()
    status = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//span[@role='menuitemcheckbox' and normalize-space()='Status']")))
    status.click()

def open_order(driver,status):
    status_xpath = f"//th[@class='o_group_name' and contains(., '{status}')]"
    quotation = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, status_xpath)))
    quotation.click()
    # order_xpath = f"(.//*[normalize-space(text()) and normalize-space(.)='{carrier_no}'])[1]/following::td[1]"
    order_xpath = "//tbody/tr[contains(@class,'o_data_row')][1]"
    element = WebDriverWait(driver,100).until(EC.element_to_be_clickable((By.XPATH, order_xpath)))
    element.click()

def confirm_order(driver):
    confirm_btn = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.NAME, "action_confirm")))
    confirm_btn.click()
    time.sleep(2)
    status = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, "//button[@data-value='order']")))
    title = status.get_attribute("title")
    assert title == "Current state"

def post_order(driver):
    post_btn = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "action_post")))
    post_btn.click()
    time.sleep(2)
    status = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//button[@data-value='posted']")))
    title = status.get_attribute("title")
    assert title == "Current state"

def cancel_order(driver):
    cancel_btn = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.NAME, "action_cancel")))
    cancel_btn.click()
    time.sleep(2)
    status = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, "//button[@data-value='cancel']")))
    title = status.get_attribute("title")
    assert title == "Current state"

def reset_order(driver):
    reset_btn = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.NAME, "action_reset")))
    reset_btn.click()
    time.sleep(2)
    status = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, "//button[@data-value='draft']")))
    title = status.get_attribute("title")
    assert title == "Current state"