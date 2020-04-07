from botbuilder.core import (
    MessageFactory,
    UserState
)
from botbuilder.dialogs import (
    DialogTurnResult,
    WaterfallDialog,
    WaterfallStepContext
)
from botbuilder.schema import (
    InputHints
)

from .cancel_and_help_dialog import CancelAndHelpDialog
from dialogs.constants import Keys, SalutationPhase
from resources import messages
from utils.logging import LOGGER


class SalutationDialog(CancelAndHelpDialog):
    def __init__(self, user_state: UserState, storage: object):
        super(SalutationDialog, self).__init__(SalutationDialog.__name__)

        self.user_state = user_state
        self.did_show_entry_msg = False
        self.storage = storage

        self.add_dialog(
            WaterfallDialog(
                Keys.WATER_FALL_DIALOG_ID.value,
                [
                    self.salute
                ],
            )
        )

        self.initial_dialog_id = Keys.WATER_FALL_DIALOG_ID.value

    async def salute(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        LOGGER.debug(msg=f"{SalutationDialog.__name__}: salute")

        dialog_options: {} = step_context.options if step_context.options is not None else {}

        salutation_phase: SalutationPhase = dialog_options.get(
            Keys.SALUTATION_PHASE.value, SalutationPhase.INITIATE
        )

        message_text = f""
        if salutation_phase == SalutationPhase.INITIATE:
            message_text = f"{messages.HELLO}! {messages.HOW_ARE_YOU_DOING}"

        elif salutation_phase == SalutationPhase.ACKNOWLEDGE:
            message_text = f"{messages.SALUTATION_ACKNOWLEDGEMENT}. {messages.HOW_CAN_I_HELP}"

        elif salutation_phase == SalutationPhase.PROMPT:
            message_text = f"{messages.HOW_CAN_I_HELP}"

        await step_context.context.send_activity(
            MessageFactory.text(
                message_text,
                message_text,
                InputHints.ignoring_input
            )
        )
        return await step_context.end_dialog(self.id)

