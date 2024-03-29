import time

from selenium.webdriver.common.by import By

from Auctions.Auction import Auction


class ZliczanieWynikow:
    def __init__(self, driver):
        self.driver = driver

    def zliczanie_wynikow(self, tab):
        i = 2
        nr = 1
        czy_koniec = False
        while not czy_koniec:
            try:
                time.sleep(0.2)

                for_search = f"//table/tbody/tr[{i}]//td[9]/a"
                link_elementu = self.driver.find_element(By.XPATH, for_search)

                for_search = f"//table/tbody/tr[{i}]//td[3]"
                data_zakonczenia = self.driver.find_element(By.XPATH, for_search)

                for_search = f"//table/tbody/tr[{i}]//td[7]"
                cena_wywolawcza = self.driver.find_element(By.XPATH, for_search)

                # Utwórz instancję klasy Auction
                new_auction = Auction(
                    link=link_elementu.get_attribute("href"),
                    data=data_zakonczenia.text,
                    cena_wywolawcza=cena_wywolawcza.text
                )

                #print(nr, "   ", new_auction.link, new_auction.data, new_auction.cena_wywolawcza)

                # Dodaj instancję do tablicy
                tab.append(new_auction)

                i += 1
                nr += 1


            except:

                try:
                    nastepna_strona = self.driver.find_element(By.PARTIAL_LINK_TEXT, 'Następna')
                    nastepna_strona.click()
                    i = 2
                    time.sleep(1)

                except:
                    czy_koniec = True
                    print("koniec stron")
