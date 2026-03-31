import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import os
import time

load_dotenv()

email = os.getenv("EMAIL")
password = os.getenv("PASSWORD")
url = os.getenv("URL")

def logout(driver):
    driver.get('https://sandbox.erp.quatrixglobal.com/')
    usermenu = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, "//span[text()='Kelvin Kiarie']")))
    usermenu.click()
    logout_btn = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, "//a[normalize-space(text())='Log out']")))
    logout_btn.click()

    
    
def test_valid_login(driver, login):
    login(email,password)
    discuss = WebDriverWait(driver,20).until(EC.visibility_of_element_located((By.XPATH, "//a[@data-menu-xmlid='mail.menu_root_discuss']")))
    assert "Discuss" in discuss.text.strip()
    logout(driver)
    time.sleep(3)
    
def test_invalid_login(driver, login):
    login("test123432@email.com", "pwd123")
    WebDriverWait(driver,10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "p.alert.alert-danger[role='alert']")))
    assert "Wrong login/password" in driver.page_source 
    
   