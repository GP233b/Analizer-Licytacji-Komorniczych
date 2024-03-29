import datetime as dt
from Connector.DatabaseConnector import DatabaseConnector

class DatabaseConnectorProxy:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(DatabaseConnectorProxy, cls).__new__(cls)
            cls._instance._db_connector = DatabaseConnector()
            cls._instance._access_log = []  # Logowanie operacji
            cls._instance._query_cache = {}  # Pamięć podręczna zapytań
            cls._instance._max_connections = 5  # Maksymalna liczba jednoczesnych połączeń
            cls._instance._current_connections = 0  # Licznik jednoczesnych połączeń
        return cls._instance

    def get_connection(self):
        # Logowanie operacji
        operation_log = {"timestamp": dt.datetime.now(), "operation": "Accessing database connection"}
        self._instance._access_log.append(operation_log)

        # Kontrola dostępu oparta na roli użytkownika
        user_role = "admin"  # Pobierz rolę użytkownika z sesji lub innych źródeł
        if user_role != "admin":
            raise PermissionError("You do not have permission to access the database.")

        # Kontrola limitów dotyczących liczby jednoczesnych połączeń
        if self._instance._current_connections >= self._instance._max_connections:
            raise ConnectionError("Maximum number of concurrent connections reached.")
        self._instance._current_connections += 1

        return self._instance._db_connector.get_connection()

    def execute_query(self, query, *args):
        # Wyczyszczenie pamięci podręcznej
        self._instance._query_cache = {}

        # Logowanie operacji
        operation_log = {"timestamp": dt.datetime.now(), "operation": f"Executing query: {query}"}
        self._instance._access_log.append(operation_log)

        # W tej wersji execute_query przyjmuje dowolną liczbę argumentów (*args)
        if query.upper().startswith("SELECT"):
            # Obsługa zapytań SELECT
            result = self._instance._db_connector.execute_query(query, *args).fetchall()
        else:
            # Obsługa innych rodzajów zapytań (UPDATE, INSERT, itp.)
            self._instance._db_connector.execute_query(query, *args)
            result = None  # Możesz zwrócić coś innego w zależności od potrzeb

        return result

    def close_connection(self):
        # Zwalnianie połączenia
        self._instance._db_connector.close_connection()

        # Obniżanie licznika jednoczesnych połączeń
        self._instance._current_connections -= 1
