from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time

class Group_Open_Order:
    def __init__(self):
        pass

    def group_orders(self,driver):
        group_by = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, "//button[@class='dropdown-toggle btn btn-light ' and .//span[normalize-space()='Group By']]")))
        group_by.click()
        status = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, "//span[@role='menuitemcheckbox' and normalize-space()='Status']")))
        status.click()

    def open_order(self,driver,status):
        status_xpath = f"//th[@class='o_group_name' and contains(., '{status}')]"
        status = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, status_xpath)))
        status.click()
        voucher_xpath = "//tbody/tr[contains(@class,'o_data_row')][1]"
        voucher = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, voucher_xpath)))
        voucher.click()
        time.sleep(3)