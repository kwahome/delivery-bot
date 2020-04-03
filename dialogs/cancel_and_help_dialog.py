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
from resources import HelpCard


CANCEL = "cancel"
END = "end"
HELP = "help"
QUESTION_MARK = "?"
QUIT = "quit"


class CancelAndHelpDialog(ComponentDialog):
    def __init__(self, dialog_id: str):
        super(CancelAndHelpDialog, self).__init__(dialog_id)

    async def on_continue_dialog(self, inner_dc: DialogContext) -> DialogTurnResult:
        result = await self.interrupt(inner_dc)
        if result is not None:
            return result

        return await super(CancelAndHelpDialog, self).on_continue_dialog(inner_dc)

    async def interrupt(self, inner_dc: DialogContext) -> DialogTurnResult:
        if inner_dc.context.activity.type == ActivityTypes.message:
            text = inner_dc.context.activity.text.lower()
            message = Activity(
                type=ActivityTypes.message,
                attachments=[
                    CardFactory.adaptive_card(HelpCard)
                ]
            )

            if text in (HELP, QUESTION_MARK):
                await inner_dc.context.send_activity(message)
                return DialogTurnResult(DialogTurnStatus.Waiting)

            if text in (CANCEL, QUIT):
                cancel_message_text = "Cancelled."
                cancel_message = MessageFactory.text(
                    cancel_message_text, cancel_message_text, InputHints.ignoring_input
                )
                await inner_dc.context.send_activity(cancel_message)
                return await inner_dc.cancel_all_dialogs()
        return None
