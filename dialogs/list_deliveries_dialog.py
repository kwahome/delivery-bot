from botbuilder.core import (
    CardFactory,
    UserState
)
from botbuilder.dialogs import (
    DialogTurnResult,
    WaterfallDialog,
    WaterfallStepContext
)
from botbuilder.schema import (
    ActivityTypes,
    Activity,
    ChannelAccount
)

from .cancel_and_help_dialog import CancelAndHelpDialog
from dialogs.constants import Keys
from domain.model import Delivery, DeliveryList
from resources import DeliveryCard, messages
from utils.logging import LOGGER


class ListDeliveriesDialog(CancelAndHelpDialog):
    def __init__(self, user_state: UserState, storage: object):
        super(ListDeliveriesDialog, self).__init__(ListDeliveriesDialog.__name__)

        self.user_state = user_state
        self.did_show_entry_msg = False
        self.storage = storage

        self.add_dialog(
            WaterfallDialog(
                Keys.WATER_FALL_DIALOG_ID.value,
                [
                    self.list_deliveries,
                ],
            )
        )

        self.initial_dialog_id = Keys.WATER_FALL_DIALOG_ID.value

    async def list_deliveries(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        LOGGER.debug(msg=f"{ListDeliveriesDialog.__name__}: list deliveries")

        recipient: ChannelAccount = step_context.context.activity.recipient

        data = await self.storage.read([recipient.id])

        # get this member's state
        member_state = data.get(recipient.id, {})

        delivery_list: DeliveryList = member_state.get(Keys.DELIVERY_LIST_STATE.value)
        if delivery_list:
            deliveries: [Delivery] = delivery_list.deliveries
            for delivery in deliveries:
                DeliveryCard["body"][0]["text"] = delivery.item
                DeliveryCard["body"][1]["text"] = delivery.destination
                DeliveryCard["body"][2]["text"] = delivery.time
                message = Activity(
                    type=ActivityTypes.message,
                    attachments=[
                        CardFactory.adaptive_card(DeliveryCard)
                    ],
                )
                await step_context.context.send_activity(message)
        else:
            await step_context.context.send_activity(messages.NO_DELIVERIES)
        return await step_context.end_dialog()

