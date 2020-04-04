from enum import Enum


class Actions(Enum):
    GREETINGS: str = "Greetings"
    EXIT: str = "Exit"
    LIST_DELIVERIES: str = "List deliveries"
    SCHEDULE_DELIVERY: str = "Schedule delivery"
    UNKNOWN: str = "Unknown"
