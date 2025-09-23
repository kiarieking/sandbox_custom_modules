from dotenv import load_dotenv
import os
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

load_dotenv()
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

def test_create_voucher(driver,login,fuel_icon):
    login(EMAIL,PASSWORD)
    fuel_icon()
    create_voucher(driver)
    fill_voucher_form(driver)
    time.sleep(4)

def create_voucher(driver):
    create_btn = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, "//span[normalize-space()='Create']")))
    create_btn.click()
    new  = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, "//li[@class='breadcrumb-item active' and normalize-space()='New']")))
    assert new.text.strip() == "New"

def fill_voucher_form(driver):
    vehicle_input = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "vehicle_id")))
    vehicle_input.click()
    new_vehicle = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.LINK_TEXT, "Mitsubishi/Mitsubishi/ExtraVehicle#1")))
    new_vehicle.click()
    lpo_number = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "lpo_voucher_number")))
    lpo_number.clear()
    lpo_number.send_keys("test123")
    driver_number = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "driver_phone_number")))
    driver_number.clear()
    driver_number.send_keys("254112291144")
    driver_number = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "driver_phone_number")))
    add_line = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[@role='button' and normalize-space(text())='Add a line']")))
    add_line.click()
    product = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "product_id")))
    product.click()
    select_product = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//a[contains(@class, "ui-menu-item-wrapper") and normalize-space(text())="[FUEL] Diesel"]')))
    select_product.click()
    description = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "description")))
    description.click()
    description.send_keys("test description")
    narration = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "narration")))
    narration.click()
    narration.send_keys("test narration")
    quantity = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "quantity")))
    quantity.click()
    quantity.send_keys('125')
    unit_price = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "price_unit")))
    unit_price.click()
    unit_price.send_keys('5')
    save_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[@class='btn btn-primary o_form_button_save' and @type='button' and @accesskey='s']")))
    save_btn.click()
    time.sleep(2)

