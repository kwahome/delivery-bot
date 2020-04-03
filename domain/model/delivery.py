from botbuilder.core import StoreItem
from datetime import datetime


class Delivery(StoreItem):
    """
    Delivery data model
    """
    def __init__(self, item: str = None, destination: str = None, time: datetime = None):
        super(Delivery, self).__init__()
        self.item: str = item
        self.destination: str = destination
        self.time: datetime = time


class DeliveryList(StoreItem):
    """
    A list of Delivery items.
    """

    def __init__(self):
        super(DeliveryList, self).__init__()
        self.deliveries: [Delivery] = []
        self.turn_number = 0
        self.e_tag = "*"
