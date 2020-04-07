from botbuilder.dialogs import (
    ComponentDialog,
    DialogContext,
    DialogTurnResult,
    DialogTurnStatus,
)
from botbuilder.schema import (
    Activity,
    ActivityTypes,
    InputHints
)
from botbuilder.core import (
    CardFactory,
    MessageFactory
)

from dialogs.constants import Prompts
from resources import HelpCard, messages
from utils.logging import LOGGER


class CancelAndHelpDialog(ComponentDialog):
    def __init__(self, dialog_id: str):
        super(CancelAndHelpDialog, self).__init__(dialog_id)

    async def on_continue_dialog(self, inner_dc: DialogContext) -> DialogTurnResult:
        LOGGER.debug(msg=f"{CancelAndHelpDialog.__name__}: on_continue_dialog")

        result = await self.interrupt(inner_dc)
        if result is not None:
            return result

        return await super(CancelAndHelpDialog, self).on_continue_dialog(inner_dc)

    async def interrupt(self, inner_dc: DialogContext) -> DialogTurnResult:
        LOGGER.debug(msg=f"{CancelAndHelpDialog.__name__}: interrupt")

        if inner_dc.context.activity.type == ActivityTypes.message:
            text = inner_dc.context.activity.text.lower()
            message = Activity(
                type=ActivityTypes.message,
                attachments=[
                    CardFactory.adaptive_card(HelpCard)
                ]
            )

            if text in (Prompts.HELP.value, Prompts.QUESTION_MARK.value):
                await inner_dc.context.send_activity(message)
                return DialogTurnResult(DialogTurnStatus.Waiting)

            if text in (Prompts.CANCEL.value, Prompts.END.value, Prompts.QUIT.value):
                cancel_message = MessageFactory.text(
                    messages.CANCELLED, messages.CANCELLED, InputHints.ignoring_input
                )
                await inner_dc.context.send_activity(cancel_message)
                await inner_dc.cancel_all_dialogs()
                return await inner_dc.replace_dialog(self.initial_dialog_id)
        return None
