from botbuilder.core import (
    CardFactory,
    MessageFactory,
    UserState
)
from botbuilder.dialogs import (
    ComponentDialog,
    DialogTurnResult,
    WaterfallDialog,
    WaterfallStepContext
)
from botbuilder.dialogs.prompts import (
    PromptOptions,
    TextPrompt,
    DateTimePrompt,
    ChoicePrompt,
    ConfirmPrompt
)
from botbuilder.schema import (
    ActivityTypes,
    Activity
)

from dialogs.constants import Dialog
from domain.model import Delivery, DeliveryList
from resources import DeliveryCard


class CreateDeliveryDialog(ComponentDialog):
    def __init__(self, user_state: UserState, storage: object):
        super(CreateDeliveryDialog, self).__init__(CreateDeliveryDialog.__name__)

        self.user_state = user_state
        self.did_show_entry_msg = False
        self.storage = storage

        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))
        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(DateTimePrompt(DateTimePrompt.__name__))
        self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))
        self.add_dialog(
            WaterfallDialog(
                Dialog.WATER_FALL_DIALOG_ID.value,
                [
                    self.item_step,
                    self.destination_step,
                    self.time_step,
                    self.confirm_step,
                    self.acknowledgement_step
                ],
            )
        )

        self.initial_dialog_id = Dialog.WATER_FALL_DIALOG_ID.value

    async def item_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        # Create an object in which to collect the delivery information within the dialog.
        step_context.values[Dialog.DELIVERY_DIALOG_STATE_KEY.value] = Delivery()

        prompt_options = PromptOptions(
            prompt=MessageFactory.text(
                "What would you like me to have delivered?"
            )
        )
        return await step_context.prompt(TextPrompt.__name__, prompt_options)

    async def destination_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        # Set the delivery item to what they entered in response to the create delivery prompt.
        delivery: Delivery = step_context.values[Dialog.DELIVERY_DIALOG_STATE_KEY.value]
        delivery.item = step_context.result

        prompt_options = PromptOptions(
            prompt=MessageFactory.text(
                f"Where do you want {delivery.item} delivered?"
            )
        )
        return await step_context.prompt(TextPrompt.__name__, prompt_options)

    async def time_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        # Set the delivery destination to what they entered in response to the destination prompt.
        delivery: Delivery = step_context.values[Dialog.DELIVERY_DIALOG_STATE_KEY.value]
        delivery.destination = step_context.result
        prompt_options = PromptOptions(
            prompt=MessageFactory.text(
                f"When do you want {delivery.item} delivered to {delivery.destination}?"
            ),
            retry_prompt=MessageFactory.text(
                f"Please enter a valid time"
            ),
        )

        return await step_context.prompt(DateTimePrompt.__name__, prompt_options)

    async def confirm_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        # Set the delivery destination to what they entered in response to the destination prompt.
        delivery: Delivery = step_context.values[Dialog.DELIVERY_DIALOG_STATE_KEY.value]

        delivery.time = step_context.result[0].value

        prompt_options = PromptOptions(
            prompt=MessageFactory.text(
                f"""I have set the delivery. 
                \nIs there anything else I can help with?"""
            )
        )

        DeliveryCard["body"][0]["text"] = f"Item: {delivery.item}"
        DeliveryCard["body"][1]["text"] = f"Destination: {delivery.destination}"
        DeliveryCard["body"][2]["text"] = f"Time: {delivery.time}"

        await step_context.context.send_activity(
            Activity(
                type=ActivityTypes.message,
                text=MessageFactory.text(
                    f"""I have set the delivery. 
                    \nIs there anything else I can help with?"""
                ),
                attachments=[
                    CardFactory.adaptive_card(DeliveryCard)
                ],
            )
        )

        return await step_context.prompt(ConfirmPrompt.__name__, prompt_options)

    async def acknowledgement_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        await self._create_delivery(step_context)
        if step_context.result:
            await step_context.context.send_activity(
                MessageFactory.text(":-)")
            )
            return await step_context.begin_dialog(self.id)
        else:
            await step_context.context.send_activity(
                MessageFactory.text("Okay, goodbye!.")
            )
        return await step_context.end_dialog()

    async def _create_delivery(self, step_context):
        delivery: Delivery = step_context.values[Dialog.DELIVERY_DIALOG_STATE_KEY.value]
        data = await self.storage.read(["DeliveryList"])
        if "DeliveryList" not in data:
            delivery_list = DeliveryList()
            delivery_list.deliveries.append(delivery.__dict__)
            delivery_list.turn_number = 1
        else:
            delivery_list: DeliveryList = data["DeliveryList"]
            delivery_list['deliveries'].append(delivery.__dict__)
            delivery_list['turn_number'] = delivery_list['turn_number'] + 1

        try:
            record = {
                "DeliveryList": delivery_list
            }
            await self.storage.write(record)
        except Exception as e:
            await step_context.context.send_activity(
                f"Sorry, something went wrong storing your message! {str(e)}")

