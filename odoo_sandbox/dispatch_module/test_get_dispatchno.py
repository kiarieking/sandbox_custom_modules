from dotenv import load_dotenv
import os
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pytest
from selenium.webdriver.common.keys import Keys

load_dotenv()
EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')

@pytest.mark.order(2)
def test_edit_dispatch(driver,login,dispatch_icon):
    login(EMAIL,PASSWORD)
    time.sleep(3)
    dispatch_icon()
    status = "Quotation"
    group_dispatch(driver)
    # dispatch_no = get_dispatch_no(driver)
    open_dispatch(driver,status)


# def get_dispatch_no(driver):
#     dispatch = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH,"(//tr[contains(@class,'o_data_row') and not(contains(@style,'display: none'))])[1]//td[@name='name']")))
#     dispatch_no = dispatch.text.strip()
#     print (dispatch_no)
#     return dispatch_no

def group_dispatch(driver):
    group_by = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, "//button[@class='dropdown-toggle btn btn-light ' and .//span[normalize-space()='Group By']]")))
    group_by.click()
    status = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, "//span[@role='menuitemcheckbox' and normalize-space()='Status']")))
    status.click()


def open_dispatch(driver,status):
    status_xpath = f"//th[@class='o_group_name' and contains(., '{status}')]"
    status = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, status_xpath)))
    status.click()
    # dispatch_xpath = f"(.//*[normalize-space(text()) and normalize-space(.)='{dispatch_no}'])[1]/following::td[1]"
    dispatch_xpath = "//tbody/tr[contains(@class,'o_data_row')][1]"
    dispatch = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, dispatch_xpath)))
    dispatch.click()
    # time.sleep(3)
