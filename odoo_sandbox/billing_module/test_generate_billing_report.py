from dotenv import load_dotenv
import os
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

load_dotenv()
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

def test_generate_billing_report(driver,login,billing_icon):
    login(EMAIL,PASSWORD)
    billing_icon()
    generate_report(driver)
    
def generate_report(driver):
        billing_report = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[normalize-space(text())='Billing Reports']")))
        billing_report.click()
        billing_ledger = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[span[text()='Billing Ledger']]")))
        billing_ledger.click()
        date_start = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "date_start")))
        date_start.click()
        select_start_date = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "(.//*[normalize-space(text()) and normalize-space(.)='Sa'])[1]/following::td[11]")))
        select_start_date.click()
        date_end = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "date_end")))
        date_end.click()
        select_end_date = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "(.//*[normalize-space(text()) and normalize-space(.)='Sa'])[1]/following::td[16]")))
        select_end_date.click()
        carrier = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "carrier_id")))
        carrier.click()
        select_carrier = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[@class='ui-menu-item-wrapper' and text()='ABDULAHI WALAIKA']")))
        select_carrier.click()
        generate_rpt_btn =WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[@class='btn btn-primary' and span[text()='Generate Report']]")))
        generate_rpt_btn.click()
        user_error_modal = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//div[@class='modal-content']//h4[@class='modal-title' and contains(text(), 'User Error')]")))
        assert user_error_modal.is_displayed
        time.sleep(2)