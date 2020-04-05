from enum import Enum


class Intent(Enum):
    CANCEL = "Cancel"
    SALUTATION = "Salutation"
    SALUTATION_ACKNOWLEDGEMENT = "SalutationAcknowledgement"
    LIST_DELIVERIES = "ListDeliveries"
    NONE_INTENT = "NoneIntent"
    SCHEDULE_DELIVERY = "ScheduleDelivery"
