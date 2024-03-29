import datetime
import copy
import traceback

from Factory.AuctionFactory import AuctionFactory
from ObserverPattern.NewAuctionObserver import NewAuctionObserver
from ObserverPattern.Subject import Subject
from PageScraper import PageScraper


class LicytacjeAnalizer:
    def __init__(self, driver, db_proxy):
        self.driver = driver
        self.db_proxy = db_proxy

        # Inicjalizacja obserwatora
        self.new_auction_observer = NewAuctionObserver(db_proxy)

        # Inicjalizacja podmiotu (Subject)
        self.subject = Subject()
        self.subject.add_observer(self.new_auction_observer)

        # Inicjalizacja scraper'a
        self.page_scraper = PageScraper(driver)

    def szukanie_slow_klucz(self, html, lista_slow):
        list_spec = [" ", ";", ",", "/", "\\", "."]
        for slowo in lista_slow:
            slowo = str(slowo)[2:len(slowo) - 4]
            for spec in list_spec:
                if (spec + slowo) in html:
                    return [True, spec + slowo]
        return [False, ""]

    def odswiezenie_bazy(self, list_of_auctions):
        # Pobierz instancję DatabaseConnectorProxy
        db_connector = self.db_proxy
        conn = db_connector.get_connection()

        auction_factory = AuctionFactory()

        try:
            # Użyj bloku with do automatycznego zarządzania połączeniem
            with conn:
                with conn.cursor() as cursor:
                    # Użyj metody execute_query z proxy
                    query = "SELECT SLW_SLOWO FROM SLOWNIK"
                    slowa_klucz = db_connector.execute_query(query)

                    # Użyj metody execute_query z proxy
                    query = "SELECT SBW_SLOWO FROM SLOWNK_ZBANOWANYCH_SLOW"
                    slowa_zbanowane = db_connector.execute_query(query)

                    # Użyj metody execute_query z proxy
                    query = "UPDATE AUKCJE_LASY SET AUK_AKTUALNA = ?"
                    db_connector.execute_query(query, (0,))

                    self.page_scraper = PageScraper(self.driver)
                    for aukcja in list_of_auctions:
                        link = aukcja.link  # Dostosuj dostęp do atrybutów obiektu Auction
                        # Użyj metody execute_query z proxy
                        auction_object = auction_factory.create_auction(link, aukcja.data, aukcja.cena_wywolawcza)
                        self.subject.notify_observers(aukcja)
                        query = "SELECT COUNT(*) FROM AUKCJE_LASY WHERE AUK_LINK = ?"
                        czy_juz_istnieje = db_connector.execute_query(query, (link,))

                        if czy_juz_istnieje[0][0] == 0:
                            html_orginal = self.page_scraper.pobierz_tekst_strony(link).lower()
                            html = copy.deepcopy(html_orginal)
                            for slowo in slowa_zbanowane:
                                slowo = str(slowo)[2:-3]
                                html = html.replace(slowo.lower(), "")
                            czy_las = self.szukanie_slow_klucz(html, slowa_klucz)

                            if czy_las[0]:
                                # Użyj metody execute_query z proxy
                                query = "INSERT INTO AUKCJE_LASY (AUK_LINK, AUK_DATA, AUK_CENA_WYWOLAWCZA, AUK_HTML, AUK_AKTUALNA, AUK_KLUCZ, AUK_DATA_DODANIA_LICYTACJI) VALUES (?, ?, ?, ?, ?, ?, ?)"
                                dzisiejsza_data_str = datetime.date.today().strftime('%Y-%m-%d')
                                values = (link, aukcja.data, aukcja.cena_wywolawcza, html_orginal, 1, czy_las[1],
                                          dzisiejsza_data_str)
                                db_connector.execute_query(query, values)

                            else:
                                # Użyj metody execute_query z proxy
                                query = "INSERT INTO AUKCJE_LASY (AUK_LINK, AUK_DATA, AUK_CENA_WYWOLAWCZA, AUK_HTML, AUK_AKTUALNA, AUK_KLUCZ, AUK_DATA_DODANIA_LICYTACJI) VALUES (?, ?, ?, ?, ?, ?, ?)"
                                dzisiejsza_data_str = datetime.date.today().strftime('%Y-%m-%d')
                                values = (
                                    link, aukcja.data, aukcja.cena_wywolawcza, html_orginal, 1, "", dzisiejsza_data_str)
                                cursor.execute(query, values)

                        else:
                            # Użyj metody execute_query z proxy
                            query = "UPDATE AUKCJE_LASY SET AUK_AKTUALNA = ? WHERE AUK_LINK = ?"
                            db_connector.execute_query(query, (1, link))

                            # Zatwierdź transakcję
                        conn.commit()

        except Exception as e:
            print("Wystąpił błąd:", str(e))
            traceback.print_exc()
            # Anuluj transakcję w przypadku błędu
            conn.rollback()

        finally:
            pass
