from botbuilder.dialogs import (
    ComponentDialog,
    WaterfallDialog,
    WaterfallStepContext,
    DialogTurnResult,
)
from botbuilder.dialogs.prompts import TextPrompt, PromptOptions
from botbuilder.core import MessageFactory
from botbuilder.schema import InputHints

from helpers.luis_helper import LuisHelper, Intent
from recognizers import MovieRecognizer


WF_DIALOG = "WFDialog"
ENTRY_MSG = "How can I help you?"
WHAT_ELSE_MSG = "What else can I do for you?"
TRY_AGAIN = ""


class MovieDialog(ComponentDialog):
    def __init__(self, luis_recognizer: MovieRecognizer):
        super(MovieDialog, self).__init__(MovieDialog.__name__)
        self._luis_recognizer = luis_recognizer
        self.did_show_entry_msg = False

        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(
            WaterfallDialog(
                WF_DIALOG,
                [
                    self.intro_step,
                    self.action_step,
                    self.final_step
                ]
            )
        )

        self.initial_dialog_id = "WFDialog"

    async def intro_step(
            self,
            step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        if not self._luis_recognizer.is_configured:
            return await step_context.next(None)
        if not self.did_show_entry_msg:
            self.did_show_entry_msg = True
            prompt_entry_message = MessageFactory.text(
                ENTRY_MSG, input_hint=InputHints.ignoring_input
            )

        else:
            prompt_entry_message = MessageFactory.text(
                WHAT_ELSE_MSG, input_hint=InputHints.ignoring_input
            )
        return await step_context.prompt(
            TextPrompt.__name__,
            PromptOptions(prompt=prompt_entry_message)
        )

    async def action_step(
            self,
            step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        if not self._luis_recognizer.is_configured:
            await step_context.context.send_activity("Movie")
            return await step_context.begin_dialog(
                "MovieDialog", None
            )

        intent, luis_result = await LuisHelper.execute_luis_query(
            self._luis_recognizer, step_context.context
        )
        if intent == Intent.TITLE:
            message = MessageFactory.text("Movie found")
            await step_context.context.send_activity(message)
            return await step_context.end_dialog()
        return await step_context.next(None)

    async def final_step(
            self,
            step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        return await step_context.replace_dialog(self.id)
