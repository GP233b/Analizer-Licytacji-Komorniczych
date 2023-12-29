from selenium import webdriver
import datetime
import openpyxl
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import pyodbc
import copy
import traceback
import re



def odswiezenie_bazy(list_of_auctions):
        # Połączenie z bazą danych
        server = 'localhost\MSSQL_DEV_GP'
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
                        query = "INSERT INTO AUKCJE_LASY (AUK_LINK, AUK_DATA, AUK_CENA_WYWOLAWCZA, AUK_HTML, AUK_AKTUALNA, AUK_KLUCZ,AUK_DATA_DODANIA_LICYTACJI) VALUES (?, ?, ?, ?, ?, ?, ?)"

                        dzisiejsza_data_str = datetime.date.today().strftime('%Y-%m-%d')
                        values = (link, aukcja[2], aukcja[3], html_orginal, 1,czy_las[1],dzisiejsza_data_str)
                        cursor.execute(query, values)
                        print(aukcja)
                    else:
                        query = "INSERT INTO AUKCJE_LASY (AUK_LINK, AUK_DATA, AUK_CENA_WYWOLAWCZA, AUK_HTML, AUK_AKTUALNA, AUK_KLUCZ,AUK_DATA_DODANIA_LICYTACJI) VALUES (?, ?, ?, ?, ?, ?, ?)"

                        dzisiejsza_data_str = datetime.date.today().strftime('%Y-%m-%d')
                        values = (link, aukcja[2], aukcja[3], html_orginal, 1, "", dzisiejsza_data_str)
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
        print("UDAło sie")



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

    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get(link)

    # Poczekaj na załadowanie strony (opcjonalnie)
    time.sleep(2)

    # Pobierz cały tekst strony
    tekst_strony = driver.page_source

    # Zamknięcie przeglądarki
    driver.quit()

    return tekst_strony


def zapis_do_pliku_xlsx():
    server = 'localhost\MSSQL_DEV_GP'
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

        query = "select AUK_LINK , AUK_DATA_BIN , AUK_CENA_WYWOLAWCZA_NUM , AUK_AKTUALNA , AUK_KLUCZ , AUK_FLAGA_ZAINTERESOWANIA , AUK_OPIS , AUK_DATA_DODANIA_LICYTACJI, AUK_DATA_DODANIA_LICYTACJI, AUK_KW_SAD, AUK_KW_NR, AUK_KW_CRC, " \
                " AUK_KW_SAD +'/'+ AUK_KW_NR +'/'+ AUK_KW_CRC  AS AUK_NR_KSIEGI " \
                "from AUKCJE_LASY "\
                "  order by 2"
                #"WHERE AUK_FLAGA_ZAINTERESOWANIA is  NULL AND AUK_AKTUALNA = 1 " \

        cursor.execute(query)

        columns = [column[0] for column in cursor.description]
        results = []
        row = cursor.fetchone()
        while row:
            result_dict = dict(zip(columns, row))
            results.append(result_dict)
            row = cursor.fetchone()

        # Tworzenie pliku Excela i zapisanie wyników zapytania
        wb = openpyxl.Workbook()
        sheet = wb.active

        headers = ["AUK_LINK" , "AUK_DATA_BIN" , "AUK_CENA_WYWOLAWCZA_NUM" , "AUK_AKTUALNA" , "AUK_KLUCZ" , "AUK_FLAGA_ZAINTERESOWANIA" , "AUK_OPIS" , "AUK_DATA_DODANIA_LICYTACJI" ,"AUK_KW_SAD" ,"AUK_KW_NR","AUK_KW_CRC", "AUK_NR_KSIEGI"]

        sheet.append(headers)

        for row in results:

            data_row = [row[column] for column in headers]
            sheet.append(data_row)


        dzisiejsza_data_str = datetime.datetime.now().strftime('%d.%m.%Y')
        file_path = f"D:\Projekty Domowe\Licytacje Komornicze_1\Pliki_Exelowe\{dzisiejsza_data_str}.xlsx"
        wb.save(file_path)
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


def szukanie_księgi_wieczystej_z_HTML():

    server = 'localhost\MSSQL_DEV_GP'
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
        query = "SELECT AUK_HTML ,AUK_LINK FROM AUKCJE_LASY WHERE AUK_KW_SAD IS NULL"
        cursor.execute(query)
        tab_query = cursor.fetchall()

        pattern = r'\w{4}/\w{8}/\w{1}'
        for html in tab_query:

            tab_Ksiegi = []

            html[0] = html[0].replace("ipts/lightbox", "")

            matches = re.findall(pattern, html[0])
            unique_matches = list(set(matches))

            if len(unique_matches) >0:
                tab_Ksiegi = unique_matches[0].split("/")



            if len(tab_Ksiegi) == 3:
                query = "UPDATE AUKCJE_LASY SET AUK_KW_SAD = ?, AUK_KW_NR = ?, AUK_KW_CRC = ? WHERE AUK_LINK = ?"
                cursor.execute(query, (tab_Ksiegi[0], tab_Ksiegi[1], tab_Ksiegi[2], html[1]))

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



def szukanie_linku_do_ksiegi(driver):
    WEB = "https://przegladarka-ekw.ms.gov.pl/eukw_prz/KsiegiWieczyste/wyszukiwanieKW?komunikaty=true&kontakt=true&okienkoSerwisowe=false"
    driver.get(WEB)

    # Połączenie z bazą danych
    server = 'localhost\MSSQL_DEV_GP'
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


        query = "SELECT AUK_KW_SAD, AUK_KW_NR, AUK_KW_CRC FROM AUKCJE_LASY WHERE AUK_LINK_DO_KSIEGI IS NULL"
        cursor.execute(query)
        ksiegi = cursor.fetchall()
        print("AA")
        for ksiega in ksiegi:
            time.sleep(1)
            sad = driver.find_element(By.XPATH, '//*[@id="kodWydzialuInput"]')
            time.sleep(1)
            sad.send_keys(ksiega[0])
            time.sleep(1)

            NR_ksiegi = driver.find_element(By.XPATH, '//*[@id="numerKsiegiWieczystej"]')
            time.sleep(1)
            NR_ksiegi.send_keys(ksiega[1])

            time.sleep(1)
            CRC = driver.find_element(By.XPATH, '//*[@id="cyfraKontrolna"]')
            time.sleep(1)
            CRC.send_keys(ksiega[2])

            button = driver.find_element(By.XPATH, '//*[@id="wyszukaj"]')
            button.click()
            time.sleep(200)


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



