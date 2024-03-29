import openpyxl
import pyodbc
import datetime
import traceback

def zapis_do_pliku_xlsx():
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
        file_path = f"C:\\Users\\Admin\\PycharmProjects\\Analizer-Licytacji-Komorniczych-Starcy\\{dzisiejsza_data_str}.xlsx"
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
