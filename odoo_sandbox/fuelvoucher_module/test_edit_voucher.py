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

@pytest.mark.order(14)
def test_edit_voucher(driver,login,fuel_icon):
    login(EMAIL,PASSWORD)
    fuel_icon()
    group_vouchers(driver)
    status = "Quotation"
    voucher_no = "FO3930"
    open_voucher(driver,status,voucher_no)
    edit_voucher(driver)


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

def edit_voucher(driver):
        edit_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[@type='button' and contains(@class, 'o_form_button_edit') and contains(., 'Edit')]")))
        edit_btn.click()
        vehicle_input = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "vehicle_id")))
        vehicle_input.click()
        new_vehicle = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.LINK_TEXT, "Mitsubishi/Mitsubishi/ExtraVehicle#1")))
        new_vehicle.click()
        lpo_number = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "lpo_voucher_number")))
        lpo_number.clear()
        lpo_number.send_keys("test123 edit")
        driver_number = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "driver_phone_number")))
        driver_number.clear()
        driver_number.send_keys("254122291144")
        driver_number = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "driver_phone_number")))     
        row = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//tr[@data-id='fuel.voucher.line_6']")))
        row.click()
        description = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "description")))
        description.click()
        description.clear()
        description.send_keys("test edit description")
        narration = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "narration")))
        narration.click()
        narration.clear()
        narration.send_keys("test edit narration")
        quantity = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "quantity")))
        quantity.click()
        quantity.clear()
        quantity.send_keys('135')
        unit_price = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "price_unit")))
        unit_price.click()
        unit_price.clear()
        unit_price.send_keys('5')
        save_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[@class='btn btn-primary o_form_button_save' and @type='button' and @accesskey='s']")))
        save_btn.click()
        time.sleep(3)
    