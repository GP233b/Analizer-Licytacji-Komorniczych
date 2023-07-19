from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
import time
import pyodbc
import copy
import traceback



def odswiezenie_bazy(list_of_auctions):
        # Połączenie z bazą danych
        server = 'PC-GP-1\PROJEKT_AUKCJE'
        database = 'Baza_licytacji_lasow'
        username = ''
        password = ''
        conn = pyodbc.connect(
            'DRIVER={SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)

        try:
            # Utworzenie kursora
            cursor = conn.cursor()

            # Rozpoczęcie transakcji
            cursor.execute("BEGIN TRANSACTION")

            # Wykonanie zapytania i pobranie wyników z Słownika słów, które nas interesują
            query = "SELECT SLW_SLOWO FROM SLOWNIK"
            cursor.execute(query)
            slowa_klucz = cursor.fetchall()

            # Wykonanie zapytania i pobranie wyników z Słownika niechcianych słów
            query = "SELECT SBW_SLOWO FROM SLOWNK_ZBANOWANYCH_SLOW"
            cursor.execute(query)
            slowa_zbanowane = cursor.fetchall()

            query = "UPDATE AUKCJE_LASY SET AUK_AKTUALNA = ?"
            cursor.execute(query, (0,))

            for aukcja in list_of_auctions:
                link = aukcja[1]
                query = "SELECT COUNT(*) FROM AUKCJE_LASY WHERE AUK_LINK = ?"
                cursor.execute(query, (link,))
                czy_juz_istnieje = cursor.fetchone()


                if czy_juz_istnieje[0] == 0:
                    html_orginal = pobierz_tekst_strony(link).lower()
                    html = copy.deepcopy(html_orginal)
                    for slowo in slowa_zbanowane:
                        slowo = str(slowo)[2:-3]
                        html = html.replace(slowo.lower(), "")
                    czy_las = szukanie_slow_klucz(html, slowa_klucz)
                    if czy_las[0]:
                        query = "INSERT INTO AUKCJE_LASY (AUK_LINK, AUK_DATA, AUK_CENA_WYWOLAWCZA, AUK_HTML, AUK_AKTUALNA, AUK_KLUCZ) VALUES (?, ?, ?, ?, ?,?)"
                        values = (link, aukcja[2], aukcja[3], html_orginal, 1,czy_las[1])
                        cursor.execute(query, values)
                        print(aukcja)
                    else:
                        query = "INSERT INTO AUKCJE_LASY (AUK_LINK, AUK_DATA, AUK_CENA_WYWOLAWCZA, AUK_HTML, AUK_AKTUALNA, AUK_KLUCZ) VALUES (?, ?, ?, ?, ?,?)"
                        values = (link, aukcja[2], aukcja[3], html_orginal, 1, "")
                        cursor.execute(query, values)

                else:

                    query = "UPDATE AUKCJE_LASY SET AUK_AKTUALNA = ? WHERE AUK_LINK = ?"
                    cursor.execute(query, (1, link))

            # Zatwierdzenie transakcji
            cursor.execute("COMMIT")


        except Exception as e:
            # Wyświetlenie błędu
            print("Wystąpił błąd:", str(e))
            traceback.print_exc()

            # Anulowanie transakcji
            cursor.execute("ROLLBACK")


        finally:

            # Zamknięcie kursora i połączenia
            conn.commit()
            cursor.close()
            conn.close()



def szukanie_slow_klucz(html,lista_slow):
    list_spec = [" ", ";", ",", "/", "\\", "."]
    for slowo in lista_slow:
        slowo = str(slowo)[2:len(slowo)-4]
        for spec in list_spec:
            if (spec + slowo) in html:
                print(spec + slowo)
                return [True , spec + slowo]
    return [False , ""]






def wyszukiwanie_podstawowe(driver,minPrice , maxPrice):
    """
    Function to choose primarly filters
    :param driver: driver to Website
    :param int minPrice: minimal Price of auction
    :param int maxPrice: maximal Price of auction
    """

    time.sleep(1)
    Typ_mienia = Select(driver.find_element(By.NAME, "Type"))
    time.sleep(1)
    Typ_mienia.select_by_visible_text('Nieruchomość')
    time.sleep(1)

    Wojewodzctwo = driver.find_element(By.NAME, "tbx-province")
    Wojewodzctwo.click()
    time.sleep(1)

    li_element = driver.find_element(By.XPATH, "//ul[contains(@class, 'poland css-map')]/li[@class='pl6']/span[@class='m']/span[@class='s1']")
    li_element.click()
    time.sleep(1)

    minimalPrice = driver.find_element(By.NAME , "PriceFrom")
    minimalPrice.send_keys(minPrice)
    time.sleep(1)
    maximalPrice = driver.find_element(By.NAME, "PriceTo")
    maximalPrice.send_keys(maxPrice)
    time.sleep(1)

    button = driver.find_element(By.CLASS_NAME,'button_next_active')
    button.click()


def zliczanie_wynikow(driver,tab):

    i = 2
    nr = 1
    czy_koniec = False
    while not czy_koniec:
        try:
            time.sleep(0.2)

            for_search = f"//table/tbody/tr[{i}]//td[9]/a"
            link_elementu = driver.find_element(By.XPATH, for_search)

            for_search = f"//table/tbody/tr[{i}]//td[3]"
            data_zakonczenia = driver.find_element(By.XPATH, for_search)

            for_search = f"//table/tbody/tr[{i}]//td[7]"
            cena_wywolawcza = driver.find_element(By.XPATH, for_search)

            #cena = cena_wywolawcza.get_text()
            print(nr , "   ",link_elementu.get_attribute("href") , data_zakonczenia.text ,cena_wywolawcza.text)
            tab.append([nr,link_elementu.get_attribute("href") , data_zakonczenia.text , cena_wywolawcza.text])
            i+=1
            nr+=1

        except:
            try:
                nastepna_strona = driver.find_element(By.PARTIAL_LINK_TEXT, 'Następna')
                nastepna_strona.click()
                i = 2
                time.sleep(1)

            except:
                czy_koniec = True
                print("koniec stron")


def pobierz_tekst_strony(link):
    # Otwarcie Strony
    PATH = "D:\ChromeDriver\chrome-win64\chrome.exe"
    service = Service(PATH)
    driver = webdriver.Chrome(service=service)
    driver.get(link)

    # Poczekaj na załadowanie strony (opcjonalnie)
    time.sleep(2)

    # Pobierz cały tekst strony
    tekst_strony = driver.page_source

    # Zamknięcie przeglądarki
    driver.quit()

    return tekst_strony