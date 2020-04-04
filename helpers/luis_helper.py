from typing import Dict

from botbuilder.core import (
    IntentScore,
    TopIntent,
    TurnContext,
    RecognizerResult
)
from .constants import Intent


def top_intent(intents: Dict[Intent, dict]) -> TopIntent:
    max_intent = Intent.NONE_INTENT
    max_value = 0.0

    for intent, value in intents:
        intent_score = IntentScore(value)
        if intent_score.score > max_value:
            max_intent, max_value = intent, intent_score.score

    return TopIntent(max_intent, max_value)


def get_intent(recognizer_result: RecognizerResult) -> str:
    intent = (
        sorted(
            recognizer_result.intents,
            key=recognizer_result.intents.get,
            reverse=True,
        )[:1][0]
        if recognizer_result.intents else None
    )
    return intent


class LuisHelper:
    @staticmethod
    async def execute_luis_query(
            luis_recognizer: object,
            turn_context: TurnContext
    ) -> (Intent, object):
        """
        Returns an object with pre-formatted LUIS results for the bot's dialogs to consume.
        """
        result = None
        intent = None

        try:
            recognizer_result = await luis_recognizer.recognize(turn_context)
            intent = get_intent(recognizer_result=recognizer_result)
        except Exception as exception:
            print(exception)

        return intent, result
