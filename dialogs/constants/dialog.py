from enum import Enum


class Dialog(Enum):
    WATER_FALL_DIALOG_ID: str = "WFDialog"
    # Key name to store the deliveries dialogs state info in the StepContext
    DELIVERY_DIALOG_STATE_KEY: str = "value-deliveries"
    DELIVERY_LIST_STATE_KEY: str = "delivery-list"
