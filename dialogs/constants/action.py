from enum import Enum


class Action(Enum):
    ACTION_PROMPT: str = "Action prompt"
    EXIT: str = "Exit"
    LIST_DELIVERIES: str = "List Deliveries"
    SALUTATION: str = "Salutation"
    SALUTATION_ACKNOWLEDGEMENT: str = "Salutation"
    SCHEDULE_DELIVERY: str = "Schedule Delivery"
    UNKNOWN: str = "Unknown"
