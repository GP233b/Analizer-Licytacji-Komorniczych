

class NewAuctionObserver:
    def __init__(self, db_proxy):
        self.db_proxy = db_proxy

    def update(self, new_auction):
        link = new_auction.link
        query = "SELECT COUNT(*) FROM AUKCJE_LASY WHERE AUK_LINK = ?"
        czy_juz_istnieje = self.db_proxy.execute_query(query, link)



        if czy_juz_istnieje[0][0] == 0:
            print(f"NOWA LICYTACJA:")
            print(f"Link: {new_auction.link}")
            print(f"Data: {new_auction.data}")
            print(f"Cena: {new_auction.cena_wywolawcza}")
            print("\n")

