from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

def test_website_link(driver):
    driver.get('https://sandbox.erp.quatrixglobal.com')
    driver.find_element(By.XPATH, "//a[@href='https://quatrixglobal.com']").click()
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "p.info")))
    msg ="Quatrix Global is a solution, much bigger than a transport service. "
    assert msg in driver.page_source