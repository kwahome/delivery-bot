from botbuilder.core import (
    MessageFactory,
    UserState
)
from botbuilder.dialogs import (
    Choice,
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

from dialogs import (
    CancelAndHelpDialog,
    CreateDeliveryDialog,
    ListDeliveriesDialog,
    SalutationDialog
)
from dialogs.constants import Action, Keys, SalutationPhase
from helpers.constants.intent import Intent
from recognizers import DeliverySchedulingRecognizer
from resources import messages
from utils.logging import LOGGER


class MainDialog(CancelAndHelpDialog):
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
        self.add_dialog(SalutationDialog(self.user_state, self.storage))
        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(
            WaterfallDialog(
                Keys.WATER_FALL_DIALOG_ID.value,
                [
                    self.intro_step,
                    self.action_step,
                    self.final_step
                ],
            )
        )

        self.initial_dialog_id = Keys.WATER_FALL_DIALOG_ID.value

    async def intro_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        LOGGER.debug(msg=f"Main dialog intro step")

        prompt_options = PromptOptions(
            prompt=MessageFactory.text(""),
            choices=[
                Choice(Action.SCHEDULE_DELIVERY.value),
                Choice(Action.LIST_DELIVERIES.value),
                Choice(Action.EXIT.value)
            ]
        )

        if not self.luis_recognizer.is_configured or self.luis_recognizer.luis_is_disabled:
            return await self._handle_luis_not_configured(step_context, prompt_options)

        return await step_context.prompt(TextPrompt.__name__, prompt_options)

    async def action_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        LOGGER.debug(msg="Main dialog action step")

        if not self.luis_recognizer.is_configured:
            # LUIS is not configured, we just use the choice step
            return await self._handle_action(
                step_context=step_context,
                action=step_context.result.value
            )

        # Call LUIS and gather any potential delivery details.
        # (Note the TurnContext has the response to the prompt.)
        intent, luis_result = await self.luis_recognizer.recognize(step_context.context)

        action: str = Action.UNKNOWN.value
        if intent == Intent.SALUTATION.value:
            action = Action.SALUTATION_ACKNOWLEDGEMENT.value

        elif intent == Intent.SALUTATION_ACKNOWLEDGEMENT.value:
            action = Action.ACTION_PROMPT.value

        elif intent == Intent.SCHEDULE_DELIVERY.value:
            action = Action.SCHEDULE_DELIVERY.value

        elif intent == Intent.LIST_DELIVERIES.value:
            action = Action.LIST_DELIVERIES.value

        elif intent == Intent.CANCEL.value:
            action = Action.EXIT.value

        return await self._handle_action(step_context=step_context, action=action)

    async def final_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        if self.luis_recognizer.is_configured and not self.luis_recognizer.luis_is_disabled:
            return await step_context.replace_dialog(self.id)
        return await step_context.end_dialog(self.id)

    async def _handle_luis_not_configured(
        self,
        step_context: WaterfallStepContext,
        prompt_options: PromptOptions
    ):
        await step_context.context.send_activity(
            MessageFactory.text(
                text=messages.LUIS_NOT_CONFIGURED_WARNING,
                input_hint=InputHints.ignoring_input,
            )
        )

        prompt_options.prompt = MessageFactory.text(messages.HOW_CAN_I_HELP)
        return await step_context.prompt(ChoicePrompt.__name__, prompt_options)

    async def _handle_action(self, step_context: WaterfallStepContext, action: str):

        if action == Action.SALUTATION.value:
            options = {
                Keys.SALUTATION_PHASE.value: SalutationPhase.INITIATE
            }
            return await step_context.begin_dialog(SalutationDialog.__name__, options)

        elif action == Action.SALUTATION_ACKNOWLEDGEMENT.value:
            options = {
                Keys.SALUTATION_PHASE.value: SalutationPhase.ACKNOWLEDGE
            }
            return await step_context.begin_dialog(SalutationDialog.__name__, options)

        elif action == Action.ACTION_PROMPT.value:
            options = {
                Keys.SALUTATION_PHASE.value: SalutationPhase.PROMPT
            }
            return await step_context.begin_dialog(SalutationDialog.__name__, options)

        elif action == Action.LIST_DELIVERIES.value:
            return await step_context.begin_dialog(ListDeliveriesDialog.__name__)

        elif action == Action.EXIT.value:
            await step_context.context.send_activity(MessageFactory.text(messages.GOODBYE))
            return await step_context.replace_dialog(self.id)

        elif action == Action.SCHEDULE_DELIVERY.value:
            return await step_context.begin_dialog(CreateDeliveryDialog.__name__)

        elif action == Action.UNKNOWN.value:
            await step_context.context.send_activity(
                MessageFactory.text(
                    messages.BOT_DID_NOT_UNDERSTAND,
                    messages.BOT_DID_NOT_UNDERSTAND,
                    InputHints.ignoring_input
                )
            )
            options = {
                Keys.SHOW_INTRO_PROMPT.value: False
            }
            return await step_context.begin_dialog(MainDialog.__name__, options)
        return await step_context.end_dialog(self.id)
