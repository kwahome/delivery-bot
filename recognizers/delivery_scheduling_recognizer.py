from botbuilder.ai.luis import (
    LuisApplication,
    LuisRecognizer
)
from botbuilder.core import (
    Recognizer,
    RecognizerResult,
    TurnContext
)

from config import DefaultConfig
from helpers import LuisHelper
from utils.logging import LOGGER


class DeliverySchedulingRecognizer(Recognizer):
    def __init__(self, configuration: DefaultConfig):
        self._recognizer = None

        self.luis_is_disabled = configuration.LUIS_IS_DISABLED
        self.luis_is_configured = (
            configuration.LUIS_APP_ID
            and configuration.LUIS_API_KEY
            and configuration.LUIS_API_HOST_NAME
        )
        if self.luis_is_configured:
            # Set the recognizer options depending on which endpoint version you want to use e.g
            # v2 or v3.
            luis_application = LuisApplication(
                configuration.LUIS_APP_ID,
                configuration.LUIS_API_KEY,
                "https://" + configuration.LUIS_API_HOST_NAME,
            )
            self._recognizer = LuisRecognizer(luis_application)
            self._recognizer.luis_trace_label = DeliverySchedulingRecognizer.__name__
            LOGGER.debug(msg="LUIS application configured and initialized")

    @property
    def is_configured(self) -> bool:
        # Returns true if luis is configured in the config.py and initialized.
        return self._recognizer is not None

    async def recognize(self, turn_context: TurnContext) -> RecognizerResult:
        return await LuisHelper.execute_luis_query(
            luis_recognizer=self._recognizer,
            turn_context=turn_context
        )
