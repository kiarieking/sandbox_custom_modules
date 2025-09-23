import pytest
from selenium.webdriver.support.ui  import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

def test_reset_password(driver):
    driver.get("https://sandbox.erp.quatrixglobal.com")
    reset_password_link = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.LINK_TEXT, "Reset Password")))
    reset_password_link.click()
    WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH,"//label[normalize-space()='Your Email']")))
    assert "Your Email" in driver.page_source
    email = driver.find_element(By.ID, "login")
    email.send_keys("kelvin.kiarie@quatrixglobal.com")
    confirm = driver.find_element(By.XPATH,"//button[normalize-space()='Confirm']")
    confirm.click()
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//p[@class='alert alert-success' and @role='status']")))
    assert "An email has been sent with credentials to reset your password" in driver.page_source
