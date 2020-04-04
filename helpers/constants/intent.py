from enum import Enum


class Intent(Enum):
    CANCEL = "Cancel"
    GREETINGS = "Greetings"
    LIST_DELIVERIES = "ListDeliveries"
    NONE_INTENT = "NoneIntent"
    SCHEDULE_DELIVERY = "ScheduleDelivery"
