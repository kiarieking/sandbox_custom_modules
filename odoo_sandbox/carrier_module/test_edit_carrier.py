from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from Group_Open_Order import Group_Open_Order
import time
import pytest
import os
from dotenv import load_dotenv


load_dotenv()
EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')

grp_opn = Group_Open_Order()

@pytest.mark.order(6)
def test_edit_carrier(login, driver, carrier_icon):
    login(EMAIL,PASSWORD)
    carrier_icon()
    status = "Quotation"
    grp_opn.group_orders(driver)
    grp_opn.open_order(driver,status)
    click_edit_button(driver)
    # edit_vehicle_registration(driver)
    edit_delivery_no(driver)
    edit_reference_no(driver)
    edit_description(driver)
    edit_quantity(driver)
    edit_cost(driver)
    save_changes(driver)
    order_no = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.NAME, "order_no")))
    assert order_no.text == "632-IAT0001378-text21"
    

def click_edit_button(driver):
    edit_btn = WebDriverWait(driver, 100).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".o_form_button_edit")))
    edit_btn.click()

def edit_vehicle_registration(driver):
    element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#o_field_input_905")))
    element.click()
    
def edit_delivery_no(driver):
    element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "order_no")))
    element.clear()
    element.send_keys("632-IAT0001378-text21")
    time.sleep(3)
    

def edit_quantity(driver):
    element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "quantity")))
    element.clear()
    element.send_keys("2")    

def edit_cost(driver):
    element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "carrier_price")))
    element.clear()
    element.send_keys("100000")

def edit_description(driver):
    element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "description")))
    element.clear()
    element.send_keys("KCJ389LZD5916:Kisumu")

def edit_reference_no(driver):
    element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "reference")))
    element.clear()
    element.send_keys("DO9429")

def save_changes(driver):
    element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[span[normalize-space(text())='Save']]")))
    element.click()
    time.sleep(3)