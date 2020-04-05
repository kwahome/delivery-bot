from enum import Enum


class Keys(Enum):
    # Key name to store the deliveries dialogs state info in the StepContext
    DELIVERY_DIALOG_STATE: str = "value-deliveries"
    DELIVERY_LIST_STATE: str = "delivery-list"
    SHOW_INTRO_PROMPT: str = "show-intro-prompt"
    SALUTATION_PHASE: str = "salutation-phase"
    WATER_FALL_DIALOG_ID: str = "WFDialog"
