from botbuilder.core import (
    CardFactory,
    MessageFactory,
    UserState
)
from botbuilder.dialogs import (
    DialogTurnResult,
    WaterfallDialog,
    WaterfallStepContext
)
from botbuilder.dialogs.prompts import (
    ChoicePrompt,
    ConfirmPrompt,
    DateTimePrompt,
    PromptOptions,
    TextPrompt,
)
from botbuilder.schema import (
    ActivityTypes,
    Activity,
    ChannelAccount,
    InputHints
)

from .cancel_and_help_dialog import CancelAndHelpDialog
from dialogs.constants import Keys
from domain.model import Delivery, DeliveryList
from resources import DeliveryCard


class CreateDeliveryDialog(CancelAndHelpDialog):
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
                Keys.WATER_FALL_DIALOG_ID.value,
                [
                    self.item_step,
                    self.destination_step,
                    self.time_step,
                    self.confirm_step,
                    self.acknowledgement_step
                ],
            )
        )

        self.initial_dialog_id = Keys.WATER_FALL_DIALOG_ID.value

    async def item_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """
        If a delivery item has not been provided, prompt for one.
        :param step_context:
        :return DialogTurnResult:
        """

        # Create an object in which to collect the delivery information within the dialog.
        step_context.values[Keys.DELIVERY_DIALOG_STATE.value] = Delivery()

        delivery: Delivery = step_context.values[Keys.DELIVERY_DIALOG_STATE.value]

        if delivery.item is None:
            message_text = f"What would you like me to have delivered?"
            prompt_options = PromptOptions(
                prompt=MessageFactory.text(
                    message_text,
                    message_text,
                    InputHints.expecting_input
                )
            )
            return await step_context.prompt(TextPrompt.__name__, prompt_options)
        return await step_context.next(delivery.item)

    async def destination_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """
        If a delivery destination has not been provided, prompt for one.
        :param step_context:
        :return DialogTurnResult:
        """
        # Set the delivery item to what they entered in response to the create delivery prompt.
        delivery: Delivery = step_context.values[Keys.DELIVERY_DIALOG_STATE.value]

        # capture the response from the previous step
        delivery.item = step_context.result

        if delivery.destination is None:
            message_text = f"Where do you want {delivery.item.lower()} delivered?"
            prompt_options = PromptOptions(
                prompt=MessageFactory.text(
                    message_text,
                    message_text,
                    InputHints.expecting_input
                )
            )
            return await step_context.prompt(TextPrompt.__name__, prompt_options)
        return await step_context.next(delivery.destination)

    async def time_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """
        If a delivery time has not been provided, prompt for one.
        :param step_context:
        :return DialogTurnResult:
        """
        # Set the delivery destination to what they entered in response to the destination prompt.
        delivery: Delivery = step_context.values[Keys.DELIVERY_DIALOG_STATE.value]

        # capture the response from the previous step
        delivery.destination = step_context.result

        if delivery.time is None:
            message_text = f"""When do you want {delivery.item.lower()} delivered to 
            {delivery.destination}?"""

            prompt_options = PromptOptions(
                prompt=MessageFactory.text(
                    message_text,
                    message_text,
                    InputHints.expecting_input
                ),
                retry_prompt=MessageFactory.text(
                    f"Please enter a valid time"
                ),
            )

        return await step_context.prompt(DateTimePrompt.__name__, prompt_options)

    async def confirm_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        # Set the delivery destination to what they entered in response to the destination prompt.
        delivery: Delivery = step_context.values[Keys.DELIVERY_DIALOG_STATE.value]

        # capture the response from the previous step
        delivery.time = step_context.result[0].value

        message_text = f"""I have set the delivery of {delivery.item.lower()} to
        {delivery.destination} at {delivery.time}. Is that all?"""

        prompt_options = PromptOptions(
            prompt=MessageFactory.text(message_text)
        )

        DeliveryCard["body"][0]["text"] = f"Item: {delivery.item}"
        DeliveryCard["body"][1]["text"] = f"Destination: {delivery.destination}"
        DeliveryCard["body"][2]["text"] = f"Time: {delivery.time}"

        await step_context.context.send_activity(
            Activity(
                type=ActivityTypes.message,
                text=MessageFactory.text(message_text),
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
                MessageFactory.text("Coolio. Goodbye!")
            )
            return await step_context.continue_dialog()
        else:
            await step_context.context.send_activity(
                MessageFactory.text("Happy to help!")
            )
            return await step_context.begin_dialog(self.id)

    async def _create_delivery(self, step_context):
        recipient: ChannelAccount = step_context.context.activity.recipient
        delivery: Delivery = step_context.values[Keys.DELIVERY_DIALOG_STATE.value]

        data = await self.storage.read([recipient.id])

        # get or initialize this member's state
        member_state = data.get(recipient.id, {})
        if not member_state:
            member_state = {
                recipient.id: {}
            }

        delivery_list: DeliveryList = member_state.get(Keys.DELIVERY_LIST_STATE.value)

        if delivery_list:
            delivery_list.deliveries.append(delivery)
            delivery_list.turn_number = delivery_list.turn_number + 1

        else:
            delivery_list = DeliveryList()
            delivery_list.deliveries.append(delivery)
            delivery_list.turn_number = 1
            member_state[recipient.id][Keys.DELIVERY_LIST_STATE.value] = delivery_list

        try:
            await self.storage.write(member_state)
        except Exception as e:
            await step_context.context.send_activity(
                f"Sorry, something went wrong storing your message! {str(e)}")

