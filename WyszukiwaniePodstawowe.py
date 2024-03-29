from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import time

class WyszukiwaniePodstawowe:
    def __init__(self, driver):
        self.driver = driver

    def wyszukiwanie_podstawowe(self, minPrice, maxPrice):
        time.sleep(10)
        Typ_mienia = Select(self.driver.find_element(By.NAME, "Type"))
        time.sleep(1)
        Typ_mienia.select_by_visible_text('Nieruchomość')
        time.sleep(1)

        Wojewodzctwo = self.driver.find_element(By.NAME, "tbx-province")
        Wojewodzctwo.click()
        time.sleep(1)

        li_element = self.driver.find_element(By.XPATH, "//ul[contains(@class, 'poland css-map')]/li[@class='pl6']/span[@class='m']/span[@class='s1']")
        li_element.click()
        time.sleep(1)

        minimalPrice = self.driver.find_element(By.NAME, "PriceFrom")
        minimalPrice.send_keys(minPrice)
        time.sleep(1)
        maximalPrice = self.driver.find_element(By.NAME, "PriceTo")
        maximalPrice.send_keys(maxPrice)
        time.sleep(1)

        button = self.driver.find_element(By.CLASS_NAME, 'button_next_active')
        button.click()

