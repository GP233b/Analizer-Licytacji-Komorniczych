import traceback

import pyodbc
import re

def szukanie_księgi_wieczystej_z_HTML():
    server = 'DESKTOP-SG0EUIT'
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