from botbuilder.core import (
    MessageFactory,
    UserState
)
from botbuilder.dialogs import (
    Choice,
    ComponentDialog,
    DialogTurnResult,
    WaterfallDialog,
    WaterfallStepContext
)
from botbuilder.dialogs.prompts import (
    ChoicePrompt,
    PromptOptions,
    TextPrompt
)
from botbuilder.schema import (
    InputHints
)

from dialogs.constants import Actions, Dialog
from dialogs import CreateDeliveryDialog, ListDeliveriesDialog
from helpers import LuisHelper
from helpers.constants.intent import Intent
from recognizers import DeliverySchedulingRecognizer


class MainDialog(ComponentDialog):
    def __init__(
            self,
            luis_recognizer: DeliverySchedulingRecognizer,
            user_state: UserState,
            storage: object
    ):
        super(MainDialog, self).__init__(MainDialog.__name__)

        self.luis_recognizer = luis_recognizer
        self.user_state = user_state
        self.did_show_entry_msg = False
        self.storage = storage

        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))
        self.add_dialog(CreateDeliveryDialog(self.user_state, self.storage))
        self.add_dialog(ListDeliveriesDialog(self.user_state, self.storage))
        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(
            WaterfallDialog(
                Dialog.WATER_FALL_DIALOG_ID.value,
                [
                    self.intro_step,
                    self.action_step,
                    self.final_step
                ],
            )
        )

        self.initial_dialog_id = Dialog.WATER_FALL_DIALOG_ID.value

    async def intro_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:

        dialog_options: {} = step_context.options if step_context.options is not None else {}

        show_intro_prompt = dialog_options.get(Dialog.SHOW_INTRO_PROMPT_KEY.value, False)

        prompt_message_text = ""
        prompt_choices = [
            Choice(Actions.SCHEDULE_DELIVERY.value),
            Choice(Actions.LIST_DELIVERIES.value),
            Choice(Actions.EXIT.value)
        ]
        if show_intro_prompt:
            prompt_message_text = f"How can I help you today?"

        prompt_options = PromptOptions(
            prompt=MessageFactory.text(
                prompt_message_text
            ),
            choices=prompt_choices
        )

        if not self.luis_recognizer.is_configured:
            return await self._handle_luis_not_configured(step_context, prompt_options)

        return await step_context.prompt(TextPrompt.__name__, prompt_options)

    async def action_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:

        if not self.luis_recognizer.is_configured:
            # LUIS is not configured, we just use the choice step
            return await self._handle_choice(
                step_context=step_context,
                action=step_context.result.value
            )

        # Call LUIS and gather any potential delivery details.
        # (Note the TurnContext has the response to the prompt.)
        intent, luis_result = await LuisHelper.execute_luis_query(
            self.luis_recognizer, step_context.context
        )

        if intent == Intent.GREETINGS.value:
            return await self._handle_choice(
                step_context=step_context,
                action=Actions.GREETINGS.value
            )

        elif intent == Intent.SCHEDULE_DELIVERY.value:
            return await self._handle_choice(
                step_context=step_context,
                action=Actions.SCHEDULE_DELIVERY.value
            )

        elif intent == Intent.LIST_DELIVERIES.value:
            return await self._handle_choice(
                step_context=step_context,
                action=Actions.LIST_DELIVERIES.value
            )

        elif intent == Intent.CANCEL.value:
            return await self._handle_choice(
                step_context=step_context,
                action=Actions.EXIT.value
            )
        else:
            return await self._handle_choice(
                step_context=step_context,
                action=Actions.UNKNOWN.value
            )

    async def final_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        return await step_context.replace_dialog(self.id)

    async def _handle_luis_not_configured(
            self,
            step_context: WaterfallStepContext,
            prompt_options: PromptOptions
    ):
        message_text = f"NOTE: LUIS is not configured."
        await step_context.context.send_activity(
            MessageFactory.text(
                text=message_text,
                input_hint=InputHints.ignoring_input,
            )
        )
        return await step_context.prompt(ChoicePrompt.__name__, prompt_options)

    async def _handle_choice(self, step_context: WaterfallStepContext, action: str):

        if action == Actions.GREETINGS.value:
            message_text = f"Hello! How can I help you today?"
            await step_context.context.send_activity(
                MessageFactory.text(
                    message_text,
                    message_text,
                    InputHints.ignoring_input
                )
            )
            return await step_context.begin_dialog(MainDialog.__name__)

        elif action == Actions.LIST_DELIVERIES.value:
            return await step_context.begin_dialog(ListDeliveriesDialog.__name__)

        elif action == Actions.EXIT.value:
            await step_context.context.send_activity(MessageFactory.text("Goodbye!"))

        elif action == Actions.SCHEDULE_DELIVERY.value:
            return await step_context.begin_dialog(CreateDeliveryDialog.__name__)

        elif action == Actions.UNKNOWN.value:
            message_text = f"Sorry, I didn't get that. Please try asking in a different way"
            await step_context.context.send_activity(
                MessageFactory.text(
                    message_text,
                    message_text,
                    InputHints.ignoring_input
                )
            )
            options = {
                Dialog.SHOW_INTRO_PROMPT_KEY.value: False
            }
            return await step_context.begin_dialog(MainDialog.__name__, options)
        return await step_context.end_dialog(self.id)

