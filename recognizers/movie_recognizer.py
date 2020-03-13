from botbuilder.ai.luis import LuisApplication, LuisRecognizer
from botbuilder.core import Recognizer, RecognizerResult, TurnContext


class MovieRecognizer(Recognizer):
    def __init__(
            self,
            luis_app_id: str,
            luis_api_key: str,
            luis_api_host_name: str,
    ):
        self._recognizer = None

        luis_is_configured = (luis_app_id and luis_api_key and luis_api_host_name)
        if luis_is_configured:
            luis_application = LuisApplication(
                luis_app_id,
                luis_api_key,
                "https://" + luis_api_host_name,
            )

            self._recognizer = LuisRecognizer(luis_application)

    @property
    def is_configured(self) -> bool:
        # Returns true if luis configured.
        return self._recognizer is not None

    async def recognize(self, turn_context: TurnContext) -> RecognizerResult:
        return await self._recognizer.recognize(turn_context)
