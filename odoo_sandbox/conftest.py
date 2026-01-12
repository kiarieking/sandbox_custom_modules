import pytest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv, find_dotenv
import os
import tempfile
import base64
import time

@pytest.fixture(scope='function')
def driver():
    service = Service('/usr/bin/chromedriver')
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    # tmp_profile_dir = "~/.config/google-chrome"
    # options.add_argument(f"--user-data-dir={tmp_profile_dir}")
    driver = webdriver.Chrome(service=service,options=options)
    yield driver
    driver.quit()
    
@pytest.fixture(scope="function")
def login(driver):
    def _login(email,password):
        load_dotenv()
        URL = os.getenv('URL')
        print(URL)
        print(type(URL))
        driver.get(URL)
        time.sleep(3)
        login_input = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.ID,"login")))
        login_input.send_keys(email)
        # driver.find_element(By.ID, "login").send_keys(email)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.XPATH, "//button[@type='submit' and contains(@class, 'btn-primary')]").click()
        time.sleep(3)
    return _login

@pytest.fixture
def dispatch_icon(driver):
    def _dispatch_icon():
        env_path = find_dotenv(".env.icons_base64img")
        load_dotenv(env_path)
        icon_dispatch = os.getenv("DISPATCH")
        if not icon_dispatch:
            raise RuntimeError("❌ DISPATCH not found or empty in .env.icons_base64img")

        print(type(icon_dispatch))
        burger = WebDriverWait(driver,60).until(EC.presence_of_element_located((By.XPATH, "//button[@title='Home Menu' and @data-hotkey='h' and .//i[contains(@class,'fa-th')]]")))
        burger.click()
        icon = WebDriverWait(driver,20).until(EC.presence_of_element_located((By.XPATH,"//a[@href='#menu_id=641&action=1044']")))
        icon.click()
        # driver.find_element(By.XPATH, icon_dispatch).click()
    return _dispatch_icon
        

@pytest.fixture
def carrier_icon(driver):
    def _carrier_icon():
        env_path = find_dotenv(".env.icons_base64img")
        load_dotenv(env_path)
        icon_carrier = os.getenv("CARRIER")
        burger = WebDriverWait(driver,60).until(EC.presence_of_element_located((By.XPATH,"//button[@title='Home Menu' and @data-hotkey='h' and .//i[contains(@class,'fa-th')]]")))
        burger.click()
        WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH,"//a[@href='#menu_id=665&action=1071']"))).click()
        # driver.find_element(By.XPATH,icon_carrier).click()
        # WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, "//li[@class='breadcrumb-item active' and text()='Carrier Quotations']")))
        # assert "Carrier Quotations" in driver.page_source
    return _carrier_icon

@pytest.fixture
def billing_icon(driver):
    def _billing_icon():
        env_path = find_dotenv(".env.icons_base64img")
        load_dotenv(env_path)
        icon_billing = os.getenv("BILLING")
        burger = WebDriverWait(driver,60).until(EC.presence_of_element_located((By.XPATH,"//button[@title='Home Menu' and @data-hotkey='h' and .//i[contains(@class,'fa-th')]]")))
        burger.click()
        # driver.find_element(By.XPATH, icon_billing).click()
        WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH,"//a[@href='#menu_id=654&action=1058']"))).click()
        # WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, "//a[normalize-space()='Billing']")))
        # assert "Billing" in driver.page_source
    return _billing_icon

@pytest.fixture
def fuel_icon(driver):
    def _fuel_icon():
        env_path = find_dotenv(".env.icons_base64img")
        load_dotenv(env_path)  
        icon_fuel = os.getenv("FUEL")
        burger = WebDriverWait(driver,60).until(EC.presence_of_element_located((By.XPATH,"//button[@title='Home Menu' and @data-hotkey='h' and .//i[contains(@class,'fa-th')]]")))
        burger.click()
        # driver.find_element(By.XPATH, icon_fuel).click()  
        WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH,"//a[@href='#menu_id=660&action=1065']"))).click()
    return _fuel_icon

@pytest.fixture
def accounting_icon(driver):
    def _accounting_icon():
        burger = WebDriverWait(driver,60).until(EC.presence_of_element_located((By.XPATH,"//button[@title='Home Menu' and @data-hotkey='h' and .//i[contains(@class,'fa-th')]]")))
        burger.click()
        WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH, "//a[@href='#menu_id=509&action=949']"))).click()
    return _accounting_icon