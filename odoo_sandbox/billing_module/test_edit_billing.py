from dotenv import load_dotenv
import os
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pytest

load_dotenv()
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

@pytest.mark.order(11)
def test_edit_billing(driver,login,billing_icon):
    login(EMAIL,PASSWORD)
    billing_icon()
    bill_no = "BO0034"
    open_bill(driver,bill_no)
    edit_bill(driver)
    time.sleep(2)

def open_bill(driver,bill_no):
    invoiced_bills = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, "//a[@class='o_menu_entry_lvl_1']//span[normalize-space()='Invoiced Bills']")))
    invoiced_bills.click()
    bill_xpath = f"(.//*[normalize-space(text()) and normalize-space(.)='{bill_no}'])[1]/following::td[1]"
    bill = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, bill_xpath)))
    bill.click()

def edit_bill(driver):
     edit_btn = WebDriverWait(driver, 100).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".o_form_button_edit")))
     edit_btn.click()
     vehicle_input = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "vehicle_id")))
     vehicle_input.click()
     search_more_vehicle = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//li[contains(@class, 'o_m2o_dropdown_option')]/a[@class='ui-menu-item-wrapper' and text()='Search More...']")))        
     search_more_vehicle.click()
     select_vehicle = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//td[@class='o_data_cell o_field_cell o_list_char' and @title='KAA703C' and text()='KAA703C']")))
     select_vehicle.click()
     customer_input = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "client_id")))
     customer_input.click()
     select_customer = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH,"//li[@class='ui-menu-item']//a[@class='ui-menu-item-wrapper' and text()='ABDULAHI WALAIKA']")))
     select_customer.click()
     reference = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "reference_number")))
     reference.clear()
     reference.send_keys("test_ref_1")
     save_btn = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Save']]")))
     save_btn.click()
     time.sleep(3)
    