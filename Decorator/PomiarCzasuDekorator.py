import time

from LicytacjeAnalizer import LicytacjeAnalizer
from WyszukiwaniePodstawowe import WyszukiwaniePodstawowe
from ZliczanieWynikow import ZliczanieWynikow


class PomiarCzasuDekorator:
    def __init__(self, funkcja):
        self.funkcja = funkcja

    def __call__(self, *args, **kwargs):
        start_time = time.time()
        wynik = self.funkcja(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time

        print(f"[POMIAR CZASU] Metoda {self.funkcja.__name__} wykonana w czasie: {execution_time:.5f} sekundy.")

        return wynik


@PomiarCzasuDekorator
def wyszukiwanie_podstawowe(przedzial_min, przedzial_max,driver):
    print("Zaczynam Wyszukiwanie podstawowe")
    wyszukiwanie_podstawowe = WyszukiwaniePodstawowe(driver)
    wyszukiwanie_podstawowe.wyszukiwanie_podstawowe(przedzial_min,przedzial_max)



@PomiarCzasuDekorator
def zliczanie_wynikow(list_of_auctions,driver):
    print("Zaczynam Zliczanie wyników")
    zliczanie_wynikow = ZliczanieWynikow(driver)
    zliczanie_wynikow.zliczanie_wynikow(list_of_auctions)


@PomiarCzasuDekorator
def odswiezenie_bazy(list_of_auctions,driver,db_proxy):
    print("Zaczynam Analize danych")
    print("Wywołano metodę odswiezenie_bazy")
    analizer = LicytacjeAnalizer(driver, db_proxy)
    analizer.odswiezenie_bazy(list_of_auctions)
