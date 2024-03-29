import pyodbc

class DatabaseConnector:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(DatabaseConnector, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True  # Zapobiega ponownemu wykonaniu inicjalizacji
            # Inicjalizacja połączenia z bazą danych
            server = 'DESKTOP-SG0EUIT'
            database = 'Baza_licytacji_lasow'
            username = ''
            password = ''
            self.conn = pyodbc.connect(
                'DRIVER={SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
            self.cursor = self.conn.cursor()

    def get_connection(self):
        return self.conn

    def execute_query(self, query, *args):
        cursor = self.conn.cursor()  # Utwórz nowy kursor

        try:
            if args:

                cursor.execute(query, args[0])
            else:
                cursor.execute(query)

            return cursor  # Zwróć obiekt kursora, a nie wynik zapytania
        finally:
            pass

    def close_connection(self):
        self.conn.close()
