

from Connector.DatabaseConnectorProxy import DatabaseConnectorProxy
from Decorator.PomiarCzasuDekorator import wyszukiwanie_podstawowe, zliczanie_wynikow, odswiezenie_bazy
from zapisDoPliku import zapis_do_pliku_xlsx
from Księgi import szukanieKsięgiWieczystej

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager


def main():
    WEB = "https://licytacje.komornik.pl/Notice/Search"
    chrome_driver_path = "C:\\Users\\Admin\\PycharmProjects\\Analizer-Licytacji-Komorniczych\\Driver\\chromedriver-win64\\chromedriver.exe"
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--start-maximized")
    chrome_service = webdriver.chrome.service.Service(chrome_driver_path)
    driver = webdriver.Chrome( options=chrome_options)

    list_of_auctions = []
    przedzial_cenowy = [0,20_000,50_000,100_000,300_000,500_000 ]
    db_proxy = DatabaseConnectorProxy()


    for i in range(1, len(przedzial_cenowy)):
        driver.get(WEB)
        wyszukiwanie_podstawowe(przedzial_cenowy[i - 1], przedzial_cenowy[i],driver)
        print(str(przedzial_cenowy[i - 1]), " - ", str(przedzial_cenowy[i]))
        zliczanie_wynikow(list_of_auctions,driver)

    print("Znaleziono: ", len(list_of_auctions), " aukcji")

    odswiezenie_bazy(list_of_auctions,driver,db_proxy)


    driver.close()
    driver.quit()

    szukanieKsięgiWieczystej();


    zapis_do_pliku_xlsx()


if __name__ == "__main__":
    main()
