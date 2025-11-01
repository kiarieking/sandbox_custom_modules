import os
from dotenv import load_dotenv
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pytest

load_dotenv()
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

@pytest.mark.order(15)
def test_confirm_dispatch(driver,login,dispatch_icon):
    status = "Quotation"
    dispatch_no = "DO10610"
    login(EMAIL,PASSWORD)
    dispatch_icon()
    group_dispatch(driver)
    open_dispatch(driver,status, dispatch_no)
    complete_delivery(driver)
    time.sleep(3)

@pytest.mark.order(16)
def test_post_dispatch(driver,login,dispatch_icon):
    status = "Dispatch Order"
    dispatch_no = "DO9030"
    login(EMAIL,PASSWORD)
    dispatch_icon()
    group_dispatch(driver)
    open_dispatch(driver,status,dispatch_no)
    post_dispatch(driver)

@pytest.mark.order(17)
def test_cancel_dispatch(driver, login, dispatch_icon):
    status = "Posted"
    dispatch_no = "DO9993"
    login(EMAIL,PASSWORD)
    dispatch_icon()
    group_dispatch(driver)
    open_dispatch(driver,status,dispatch_no)
    cancel_dispatch(driver)


def group_dispatch(driver):
    group_by = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, "//i[@class='fa fa-bars']/following-sibling::span[text()='Group By']")))
    group_by.click()
    status = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, "//a[@aria-checked='false' and @role='menuitemcheckbox' and text()='Status']")))
    status.click()
    # time.sleep(3)

def open_dispatch(driver,status,dispatch_no):
    status_xpath = f"//th[@class='o_group_name' and contains(., '{status}')]"
    quotation = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, status_xpath)))
    quotation.click()
    order_xpath = f"(.//*[normalize-space(text()) and normalize-space(.)='{dispatch_no}'])[1]/following::td[1]"
    element = WebDriverWait(driver,100).until(EC.element_to_be_clickable((By.XPATH, order_xpath)))
    element.click()
    time.sleep(3)

def complete_delivery(driver):
    edit_btn = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//span[normalize-space()='Edit']")))
    edit_btn.click()
    time.sleep(5)
    pod_input = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, "//input[@type='file' and @name='ufile']")))
    pod_input.send_keys("/home/kkiarie/Downloads/sample.pdf")
    time.sleep(5)
    save_btn = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH, "//button[@type='button' and contains(@class, 'o_form_button_save')]")))
    save_btn.click()
    time.sleep(5)                                          
    complete_btn = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.NAME, "action_confirm")))
    complete_btn.click()
    time.sleep(5)
    status = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, "//button[@data-value='order']")))
    title = status.get_attribute("title")
    assert title == "Current state"

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



