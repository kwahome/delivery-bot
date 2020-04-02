from botbuilder.core import StoreItem
from datetime import datetime


class Delivery(StoreItem):
    """
    Delivery data model
    """
    def __init__(
            self,
            item: str = None,
            destination: str = None,
            time: str = None
    ):
        super(Delivery, self).__init__()
        self.item: str = item
        self.destination: str = destination
        self.time: str = self._validate_time(time) if time else None

    def __lt__(self, other):
        return self.datetime < other.datetime

    @property
    def datetime(self):
        return datetime.strptime(self.time, "%Y-%m-%d %H:%M")

    @staticmethod
    def _validate_time(time):
        try:
            time_format = "%Y-%m-%d %H:%M:%S"
            formatted_time = ""
            if ":" in time and time.index(":") == 2:
                t = time.split(":")
                date_time = datetime.now().replace(hour=int(t[0]), minute=int(t[1]), second=0)
                formatted_time = datetime.strftime(date_time, time_format)
            elif ":" not in time:
                date_time = datetime.strptime(time, "%Y-%m-%d").replace(hour=0, minute=0, second=0)
                formatted_time = datetime.strftime(date_time, time_format)
            elif time.index("-") == 4:
                date_time = datetime.strptime(time, time_format)
                formatted_time = datetime.strftime(date_time, time_format)
            return formatted_time[:formatted_time.rfind(":")]
        except Exception as e:
            print("Invalid time: ", time)


class DeliveryList(StoreItem):
    """
    A list of Delivery items.
    """

    def __init__(self):
        super(DeliveryList, self).__init__()
        self.deliveries: [Delivery] = []
        self.turn_number = 0
        self.e_tag = "*"
