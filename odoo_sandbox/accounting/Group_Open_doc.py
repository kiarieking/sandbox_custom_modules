from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
class Group_Open_doc:
    def __init__(self):
        pass

    def group_by(self,driver,doc_type):
        customers_btn = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH, "//button[.//span[normalize-space()='Customers']]")))
        customers_btn.click()
        invoices = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH,f"//a[normalize-space()='{doc_type}']")))
        invoices.click()
        WebDriverWait(driver,15).until(
            EC.visibility_of_element_located(
                (By.XPATH, f"//li[contains(@class,'breadcrumb-item') and contains(@class,'active')]//span[normalize-space()='{doc_type}']")
            )
        )

        group_by_btn = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH,"//span[@class='o_dropdown_title' and normalize-space()='Group By']")))
        group_by_btn.click()
        status = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH, "//span[@role='menuitemcheckbox' and normalize-space()='Status']")))
        status.click()

    def open_doc(self,driver,status):
        status_xpath = f"//th[@class='o_group_name' and contains(normalize-space(), '{status}')]"
        invoice_grp = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH,status_xpath)))
        invoice_grp.click()
        wait = WebDriverWait(driver, 20)
        wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//tbody//tr[contains(@class,'o_data_row')]")
            )
        )

        first_invoice_xpath = (
            "(//tbody//tr[contains(@class,'o_data_row')]"
            "//td[@name='name'])[1]"
        )

        # WAIT: element is visible (NOT clickable)
        invoice = wait.until(
            EC.visibility_of_element_located((By.XPATH, first_invoice_xpath))
        )
        invoice.click()

        
