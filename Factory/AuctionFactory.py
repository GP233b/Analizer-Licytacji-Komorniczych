from datetime import datetime

from Auctions.Auction import Auction


class AuctionFactory:
    @staticmethod
    def create_auction(link, data, cena):
        return Auction(link, data, cena)
