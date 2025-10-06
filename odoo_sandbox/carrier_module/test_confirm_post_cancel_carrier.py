from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from dotenv import load_dotenv
import os
import time
import pytest

load_dotenv()
EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')

@pytest.mark.order(7)
def test_confirm_order(driver,login,carrier_icon):
    status = "Quotation"
    carrier_no = "CO12825"
    login(EMAIL,PASSWORD)
    carrier_icon()
    group_orders(driver)
    open_order(driver,status,carrier_no)
    confirm_order(driver)
    time.sleep(2)

@pytest.mark.order(8)
def test_post_order(driver,login,carrier_icon):
    status = "Order"
    carrier_no = "CO12778"
    carrier_icon()
    group_orders(driver)
    open_order(driver,status,carrier_no)
    post_order(driver)
    time.sleep(2)

@pytest.mark.order(9)
def test_cancel_order(driver,login,carrier_icon):
    status = "Posted"
    carrier_no = "CO12753" 
    carrier_icon()
    group_orders(driver)
    open_order(driver,status,carrier_no)
    cancel_order(driver)
    time.sleep(2)

@pytest.mark.order(10)
def test_reset_order(driver,carrier_icon):
    status = "Cancelled"
    carrier_no = "CO12840"
    carrier_icon()
    group_orders(driver)
    open_order(driver,status,carrier_no)
    reset_order(driver)
    time.sleep(2)

def group_orders(driver):
    group_by = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//i[@class='fa fa-bars']/following-sibling::span[text()='Group By']")))
    group_by.click()
    status = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//a[@aria-checked='false' and @role='menuitemcheckbox' and text()='Status']")))
    status.click()

def open_order(driver,status,carrier_no):
    status_xpath = f"//th[@class='o_group_name' and contains(., '{status}')]"
    quotation = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, status_xpath)))
    quotation.click()
    order_xpath = f"(.//*[normalize-space(text()) and normalize-space(.)='{carrier_no}'])[1]/following::td[1]"
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