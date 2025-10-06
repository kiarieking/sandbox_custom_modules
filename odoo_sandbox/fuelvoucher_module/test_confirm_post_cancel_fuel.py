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

@pytest.mark.order(15)
def test_confirm_voucher(driver,login,fuel_icon):
    login(EMAIL,PASSWORD)
    fuel_icon()
    group_vouchers(driver)
    status = "Quotation"
    voucher_no = "FO3931"
    open_voucher(driver,status,voucher_no)
    confirm_voucher(driver)

@pytest.mark.order(16)
def test_post_voucher(driver,login,fuel_icon):
    # login(EMAIL,PASSWORD)
    fuel_icon()
    group_vouchers(driver)
    status = "Fuel Order"
    voucher_no = "FO3911"
    open_voucher(driver,status,voucher_no)

@pytest.mark.order(17)
def test_cancel_voucher(driver,login,fuel_icon):
    # login(EMAIL,PASSWORD)
    fuel_icon()
    group_vouchers(driver)
    status = "Fuel Order"
    voucher_no = "FO3737"
    open_voucher(driver,status,voucher_no)

    

def group_vouchers(driver):
    group_by = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, "//i[@class='fa fa-bars']/following-sibling::span[text()='Group By']")))
    group_by.click()
    status = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, "//a[@aria-checked='false' and @role='menuitemcheckbox' and text()='Status']")))
    status.click()

def open_voucher(driver,status,voucher_no):
    status_xpath = f"//th[@class='o_group_name' and contains(., '{status}')]"
    status = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, status_xpath)))
    status.click()
    voucher_xpath = f"(.//*[normalize-space(text()) and normalize-space(.)='{voucher_no}'])[1]/following::td[1]"
    voucher = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, voucher_xpath)))
    voucher.click()
    time.sleep(3)

def confirm_voucher(driver):
        status = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//button[@data-value='draft' and contains(@class, 'o_arrow_button') and text()[contains(., 'Quotation')]]")))
        title = status.get_attribute("title")
        print(title)
        if(title=="Current state"):
            confirm = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "action_confirm")))
            confirm.click()
        else:
            print("status is " + str(title))

        time.sleep(3)

def post_voucher(driver):
    fuelorder_grp = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//th[@class='o_group_name' and contains(text(), 'Fuel Order')]")))
    fuelorder_grp.click()
    fuel_order = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH, '//td[@class="o_data_cell o_field_cell o_list_char o_readonly_modifier o_required_modifier" and text()="FO3325"]')))
    fuel_order.click()
    status = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//button[@data-value='order' and contains(@class, 'o_arrow_button') and text()[contains(., 'Fuel Order')]]")))
    title = status.get_attribute('title')
    if(title == "Current state"):
        post_btn = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "action_post")))
        post_btn.click()
        time.sleep(3)
    else:
        print("fuel order is not " + str(title))
    time.sleep(5)
    
def cancel_voucher(driver):
        fuelorder_grp = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//th[@class='o_group_name' and contains(text(), 'Fuel Order')]")))
        fuelorder_grp.click()
        fuel_order = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH, '//td[@class="o_data_cell o_field_cell o_list_char o_readonly_modifier o_required_modifier" and text()="FO3323"]')))
        fuel_order.click()
        status = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//button[@data-value='order' and contains(@class, 'o_arrow_button') and text()[contains(., 'Fuel Order')]]")))
        title = status.get_attribute('title')
        if(title=="Current state"):
            cancel = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.NAME, "action_cancel")))
            cancel.click()
            time.sleep(3)
        else:
            print("fuel order is not " + str(title))
