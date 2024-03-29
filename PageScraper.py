import time

class PageScraper:
    def __init__(self, driver):
        self.driver = driver

    def pobierz_tekst_strony(self, link):
        self.driver.get(link)
        time.sleep(2)
        return self.driver.page_source