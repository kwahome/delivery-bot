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
    PromptOptions,
    ChoicePrompt
)

from dialogs.constants import Actions, Dialog
from dialogs import CreateDeliveryDialog, ListDeliveriesDialog


class MainDialog(ComponentDialog):
    def __init__(self, user_state: UserState, storage: object):
        super(MainDialog, self).__init__(MainDialog.__name__)

        self.user_state = user_state
        self.did_show_entry_msg = False
        self.storage = storage

        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))
        self.add_dialog(CreateDeliveryDialog(self.user_state, self.storage))
        self.add_dialog(ListDeliveriesDialog(self.user_state, self.storage))
        self.add_dialog(
            WaterfallDialog(
                Dialog.WATER_FALL_DIALOG_ID.value,
                [
                    self.intro_step,
                    self.action_step
                ],
            )
        )

        self.initial_dialog_id = Dialog.WATER_FALL_DIALOG_ID.value

    async def intro_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        prompt_options = PromptOptions(
                prompt=MessageFactory.text("How may I help you?"),
                choices=[
                    Choice(Actions.CREATE_DELIVERY.value),
                    Choice(Actions.LIST_DELIVERIES.value),
                    Choice(Actions.EXIT.value)
                ]
            )
        return await step_context.prompt(ChoicePrompt.__name__, prompt_options)

    async def action_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:

        action = step_context.result.value
        if action == Actions.CREATE_DELIVERY.value:
            return await step_context.begin_dialog(CreateDeliveryDialog.__name__)

        elif action == Actions.LIST_DELIVERIES.value:
            return await step_context.begin_dialog(ListDeliveriesDialog.__name__)

        elif action == Actions.EXIT.value:
            await step_context.context.send_activity(MessageFactory.text("Goodbye!"))
            return await step_context.end_dialog()
        else:
            return await self.intro_step(step_context)

