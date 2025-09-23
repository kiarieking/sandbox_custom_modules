from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time


def test_create_carrier(login, driver, carrier_icon):
    email = "kelvin.kiarie@quatrixglobal.com"
    password = "$kingara120"
    login(email,password)
    carrier_icon()

    group_orders(driver)
    open_order(driver)
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

def group_orders(driver):
    group_by = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//i[@class='fa fa-bars']/following-sibling::span[text()='Group By']")))
    group_by.click()
    status = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//a[@aria-checked='false' and @role='menuitemcheckbox' and text()='Status']")))
    status.click()
    

def open_order(driver):
    quotation = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//th[@class='o_group_name' and contains(., 'Quotation')]")))
    quotation.click()
    element = WebDriverWait(driver,100).until(EC.element_to_be_clickable((By.XPATH, "(.//*[normalize-space(text()) and normalize-space(.)='CO12809'])[1]/following::td[1]")))
    element.click()
    

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