import pytest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv
import os
import tempfile

@pytest.fixture(scope='session')
def driver():
    service = Service('/usr/bin/chromedriver')
    temp_profile = tempfile.mkdtemp()
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f"--user-data-dir={temp_profile}")
    driver = webdriver.Chrome(service=service)
    yield driver
    driver.quit()
    
@pytest.fixture(scope="session")
def login(driver):
    def _login(email,password):
        load_dotenv()
        URL = os.getenv('URL')
        driver.get(URL)
        
        driver.find_element(By.ID, "login").send_keys(email)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.XPATH, "//button[@type='submit' and contains(@class, 'btn-primary')]").click()
    return _login

@pytest.fixture
def dispatch_icon(driver):
    def _dispatch_icon():
        load_dotenv(".env.icons_base64img")
        icon_dispatch = os.getenv("DISPATCH")
        burger = WebDriverWait(driver,60).until(EC.presence_of_element_located((By.XPATH,"(.//*[normalize-space(text()) and normalize-space(.)='Discuss'])[1]/preceding::a[1]")))
        burger.click()
        driver.find_element(By.XPATH, icon_dispatch).click()
    return _dispatch_icon
        

@pytest.fixture
def carrier_icon(driver):
    def _carrier_icon():
        load_dotenv(".env.icons_base64img")
        icon_carrier = os.getenv("CARRIER")
        burger = WebDriverWait(driver,60).until(EC.presence_of_element_located((By.XPATH,"(.//*[normalize-space(text()) and normalize-space(.)='Discuss'])[1]/preceding::a[1]")))
        burger.click()
        driver.find_element(By.XPATH,icon_carrier).click()
        WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, "//li[@class='breadcrumb-item active' and text()='Carrier Quotations']")))
        assert "Carrier Quotations" in driver.page_source
    return _carrier_icon

@pytest.fixture
def billing_icon(driver):
    def _billing_icon():
        load_dotenv(".env.icons_base64img")
        icon_billing = os.getenv("BILLING")
        burger = WebDriverWait(driver,60).until(EC.presence_of_element_located((By.XPATH,"(.//*[normalize-space(text()) and normalize-space(.)='Discuss'])[1]/preceding::a[1]")))
        burger.click()
        driver.find_element(By.XPATH, icon_billing).click()
        WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, "//a[normalize-space()='Billing']")))
        assert "Billing" in driver.page_source
    return _billing_icon

@pytest.fixture
def fuel_icon(driver):
    def _fuel_icon():
        load_dotenv(".env.icons_base64img")  
        icon_fuel = os.getenv("FUEL")
        burger = WebDriverWait(driver,60).until(EC.presence_of_element_located((By.XPATH,"(.//*[normalize-space(text()) and normalize-space(.)='Discuss'])[1]/preceding::a[1]")))
        burger.click()
        driver.find_element(By.XPATH, icon_fuel).click()  
    return _fuel_icon