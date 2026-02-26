from dotenv import load_dotenv
import os
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from Group_Open_Order import Group_Open_Order
import pytest
from selenium.webdriver.common.keys import Keys

load_dotenv()
EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')

grp_opn = Group_Open_Order()

@pytest.mark.order(2)
def test_edit_dispatch(driver,login,dispatch_icon):
    login(EMAIL,PASSWORD)
    dispatch_icon()
    status = "Quotation"
    grp_opn.group_orders(driver)
    grp_opn.open_order(driver,status)
    start_editing_dispatch(driver)
    edit_shipper(driver)
    edit_vehicle(driver)
    edit_product_line(driver)


def group_dispatch(driver):
    group_by = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, "//button[@class='dropdown-toggle btn btn-light ' and .//span[normalize-space()='Group By']]")))
    group_by.click()
    status = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, "//span[@role='menuitemcheckbox' and normalize-space()='Status']")))
    status.click()


def open_dispatch(driver,status):
    status_xpath = f"//th[@class='o_group_name' and contains(., '{status}')]"
    status = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, status_xpath)))
    status.click()
    dispatch_xpath = "//tbody/tr[contains(@class,'o_data_row')][1]"
    dispatch = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, dispatch_xpath)))
    dispatch.click()
    # time.sleep(3)

def start_editing_dispatch(driver):
    edit_btn = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, "//button[normalize-space()='Edit']")))
    edit_btn.click()

def edit_shipper(driver):
    shipper_input = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH,"//input[contains(@class,'ui-autocomplete-input') and contains(@class,'o_input')]")))
    shipper_input.click()
    new_shipper = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@class,'dropdown-item') and normalize-space()='KEDA CERAMICS INTERNATIONAL COMPANY LIMITED']")))
    new_shipper.click()
    time.sleep(2)

def edit_vehicle(driver):
    vehicle_input = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "vehicle_id")))
    vehicle_input.click()
    new_vehicle = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.LINK_TEXT, "Mitsubishi/Mitsubishi/ExtraVehicle#1")))
    new_vehicle.click()
    time.sleep(2)

def edit_product_line(driver):
    # add_line = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.LINK_TEXT, "Add a line")))
    # add_line.click()
    product_input = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH, "//td[@name='product_id' and contains(@class, 'o_list_many2one')]")))
    product_input.click()
    product_input.click()
    product = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, '//a[normalize-space()="[KEDA] CHAVAKALI 28T"]')))
    product.click()
    delivery_no = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH, "//input[@name='order_no' and @type='text' and contains(@class, 'o_quick_editable')]")))
    delivery_no.send_keys("edit")   
    description = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, "//textarea[@name='description' and contains(@class,'o_quick_editable')]")))
    description.click()
    description.send_keys("edit description")
    narration = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, "//textarea[@name='notes' and contains(@class,'o_field_text')]")))
    narration.click()
    narration.send_keys("edit narration")
    time.sleep(3)
    quantity = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, "//input[@name='quantity' and contains(@class,'o_field_float')]")))
    quantity.click()
    quantity.send_keys("2")
    unit_price = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, "//input[@name='price_unit' and contains(@class,'o_field_float')]")))
    unit_price.click()
    unit_price.send_keys("50")
    carrier_charge = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, "//input[@name='carrier_price' and contains(@class,'o_field_float')]")))
    carrier_charge.send_keys("200")
    save_btn = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//span[@class='d-none d-sm-inline' and normalize-space(text())='Save']")))
    save_btn.click()
    time.sleep(2)




