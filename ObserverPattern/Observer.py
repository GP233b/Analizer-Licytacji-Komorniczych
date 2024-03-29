from abc import ABC, abstractmethod
# Klasa abstrakcyjna reprezentująca Obserwatora
class Observer(ABC):
    @abstractmethod
    def update(self, new_auction):
        pass