from dotenv import load_dotenv
import os
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

load_dotenv()
EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')

def test_create_dispatch(driver,login,dispatch_icon):
    login(EMAIL,PASSWORD)
    dispatch_icon()
    status = "Quotation"
    dispatch_no = "DO10613"
    group_dispatch(driver)
    open_dispatch(driver,status,dispatch_no)
    start_editing_dispatch(driver)
    edit_shipper(driver)
    edit_vehicle(driver)
    edit_product_line(driver)


def group_dispatch(driver):
    group_by = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, "//i[@class='fa fa-bars']/following-sibling::span[text()='Group By']")))
    group_by.click()
    status = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, "//a[@aria-checked='false' and @role='menuitemcheckbox' and text()='Status']")))
    status.click()
    # time.sleep(3)


def open_dispatch(driver,status,dispatch_no):
    status_xpath = f"//th[@class='o_group_name' and contains(., '{status}')]"
    status = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, status_xpath)))
    status.click()
    dispatch_xpath = f"(.//*[normalize-space(text()) and normalize-space(.)='{dispatch_no}'])[1]/following::td[1]"
    dispatch = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, dispatch_xpath)))
    dispatch.click()
    # time.sleep(3)

def start_editing_dispatch(driver):
    edit_btn = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, "//button[normalize-space()='Edit']")))
    edit_btn.click()

def edit_shipper(driver):
    shipper_input = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME,"partner_id")))
    shipper_input.click()
    new_shipper = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, "KEDA CERAMICS INTERNATIONAL COMPANY LIMITED")))
    new_shipper.click()
    time.sleep(2)

def edit_vehicle(driver):
    vehicle_input = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "vehicle_id")))
    vehicle_input.click()
    new_vehicle = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.LINK_TEXT, "Mitsubishi/Mitsubishi/ExtraVehicle#1")))
    new_vehicle.click()
    time.sleep(2)

def edit_product_line(driver):
    add_line = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.LINK_TEXT, "Add a line")))
    add_line.click()
    product_input = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.NAME, "product_id")))
    product_input.click()
    product = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.LINK_TEXT, "[KEDA] CHAVAKALI 28T")))
    product.click()
    delivery_no = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.NAME, "order_no")))
    delivery_no.send_keys("edit")
    description = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.NAME, "description")))
    description.send_keys("edit description")
    narration = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.NAME, "notes")))
    narration.click()
    narration.send_keys("edit narration")
    quantity = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.NAME, "quantity")))
    quantity.click()
    quantity.send_keys("2")
    unit_price = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.NAME, "price_unit")))
    unit_price.click()
    unit_price.send_keys("50")
    carrier_charge = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.NAME, "carrier_price")))
    carrier_charge.click()
    carrier_charge.send_keys("200")
    save_btn = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//span[@class='d-none d-sm-inline' and normalize-space(text())='Save']")))
    save_btn.click()
    time.sleep(2)




