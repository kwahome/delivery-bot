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
    Activity
)

from .cancel_and_help_dialog import CancelAndHelpDialog
from dialogs.constants import Dialog
from domain.model import Delivery, DeliveryList
from resources import DeliveryCard


class ListDeliveriesDialog(CancelAndHelpDialog):
    def __init__(self, user_state: UserState, storage: object):
        super(ListDeliveriesDialog, self).__init__(ListDeliveriesDialog.__name__)

        self.user_state = user_state
        self.did_show_entry_msg = False
        self.storage = storage

        self.add_dialog(
            WaterfallDialog(
                Dialog.WATER_FALL_DIALOG_ID.value,
                [
                    self.list_deliveries,
                ],
            )
        )

        self.initial_dialog_id = Dialog.WATER_FALL_DIALOG_ID.value

    async def list_deliveries(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        data = await self.storage.read([Dialog.DELIVERY_LIST_STATE_KEY.value])
        delivery_list: DeliveryList = data.get(Dialog.DELIVERY_LIST_STATE_KEY.value)
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
            await step_context.context.send_activity("You have no deliveries")
        return await step_context.end_dialog()

