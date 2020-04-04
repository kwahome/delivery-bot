from botbuilder.core import (
    ActivityHandler,
    ConversationState,
    UserState,
    TurnContext
)
from botbuilder.dialogs import Dialog
from botbuilder.schema import ChannelAccount
from helpers.dialog_helper import DialogHelper
from typing import List


DIALOG_STATE = "DialogState"
DELIVERIES_HISTORY = "DeliveryHistory"


class DeliveryBot(ActivityHandler):
    """ DeliveryBot activity handler"""

    def __init__(
            self,
            conversation_state: ConversationState,
            dialog: Dialog,
            user_state: UserState,
    ):
        if conversation_state is None:
            raise Exception(
                "[DeliveryBot]: Missing parameter. conversation_state is required"
            )
        if user_state is None:
            raise Exception("[DeliveryBot]: Missing parameter. user_state is required")
        if dialog is None:
            raise Exception("[DeliveryBot]: Missing parameter. dialog is required")

        self.conversation_state = conversation_state
        self.dialog = dialog
        self.user_state = user_state
        self.user_state_accessor = self.user_state.create_property(DELIVERIES_HISTORY)

    async def on_turn(self, turn_context: TurnContext):
        await super().on_turn(turn_context)
        await self.conversation_state.save_changes(turn_context, False)
        await self.user_state.save_changes(turn_context, False)

    async def on_message_activity(self, turn_context: TurnContext):
        return await DialogHelper.run_dialog(
            self.dialog,
            turn_context,
            self.conversation_state.create_property(DIALOG_STATE)
        )

    async def on_members_added_activity(
            self,
            members_added: List[ChannelAccount],
            turn_context: TurnContext
    ):
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                await turn_context.send_activity(
                    f"Hello there {member.name}! I'm the Deliveries-Bot."
                )
        return await DialogHelper.run_dialog(
            self.dialog,
            turn_context,
            self.conversation_state.create_property(DIALOG_STATE),
        )
