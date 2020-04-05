from enum import Enum


class SalutationPhase(Enum):
    ACKNOWLEDGE: str = "acknowledge"
    INITIATE: str = "initiate"
    PROMPT: str = "prompt"
