import os
from dotenv import load_dotenv
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from Group_Open_Order import Group_Open_Order
import pytest

load_dotenv()
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
POD_PATH = os.getenv("POD_PATH")


grp_opn = Group_Open_Order()

@pytest.mark.order(15)
def test_confirm_dispatch(driver,login,dispatch_icon):
    status = "Quotation"
    login(EMAIL,PASSWORD)
    dispatch_icon()
    grp_opn.group_orders(driver)
    grp_opn.open_order(driver,status)
    complete_delivery(driver)
    time.sleep(5)

@pytest.mark.order(16)
def test_post_dispatch(driver,login,dispatch_icon):
    status = "Dispatch Order"
    login(EMAIL,PASSWORD)
    dispatch_icon()
    grp_opn.group_orders(driver)
    grp_opn.open_order(driver,status)
    post_dispatch(driver)

@pytest.mark.order(17)
def test_cancel_dispatch(driver, login, dispatch_icon):
    status = "Posted"
    login(EMAIL,PASSWORD)
    dispatch_icon()
    grp_opn.group_orders(driver)
    grp_opn.open_order(driver,status)
    cancel_dispatch(driver)


def group_dispatch(driver):
    group_by = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, "//button[@class='dropdown-toggle btn btn-light ' and .//span[normalize-space()='Group By']]")))
    group_by.click()
    status = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, "//span[@role='menuitemcheckbox' and normalize-space()='Status']")))
    status.click()
    # time.sleep(3)

def open_dispatch(driver,status):
    status_xpath = f"//th[@class='o_group_name' and contains(., '{status}')]"
    quotation = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, status_xpath)))
    quotation.click()
    dispatch_xpath = "//tbody/tr[contains(@class,'o_data_row')][1]"
    element = WebDriverWait(driver,100).until(EC.element_to_be_clickable((By.XPATH, dispatch_xpath)))
    element.click()
    time.sleep(3)

def complete_delivery(driver):
    edit_btn = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//span[normalize-space()='Edit']")))
    edit_btn.click()
    time.sleep(5)
    pod_input = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, "//input[@type='file' and @name='ufile']")))
    pod_input.send_keys(POD_PATH)
    time.sleep(5)
    wait = WebDriverWait(driver,15)
    wait.until(
    EC.invisibility_of_element_located(
        (By.CSS_SELECTOR, "main.modal-body")
    )
        )
    save_btn = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH, "//button[@type='button' and contains(@class, 'o_form_button_save')]")))
    save_btn.click()
    time.sleep(5)                                          
    complete_btn = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.NAME, "action_confirm")))
    complete_btn.click()
    time.sleep(5)
    status = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, "//button[@data-value='order']")))
    title = status.get_attribute("title")
    assert title == "Current state"
    time.sleep(3)

def post_dispatch(driver):
    post_btn = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.NAME, "action_post")))
    post_btn.click()
    time.sleep(5)
    status = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, "//button[@data-value='posted']")))
    title = status.get_attribute("title")
    assert title == "Current state"
    time.sleep(3)

def cancel_dispatch(driver):
    cancel_btn = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.NAME, "action_cancel")))
    cancel_btn.click()
    time.sleep(5)
    status = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, "//button[@data-value='cancel']")))
    title = status.get_attribute("title")
    assert title == "Current state"
    time.sleep(3)    



