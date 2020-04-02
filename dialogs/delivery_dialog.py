from botbuilder.core import (
    CardFactory,
    MemoryStorage,
    MessageFactory,
    UserState
)
from botbuilder.dialogs import (
    Choice,
    ComponentDialog,
    DialogContext,
    DialogTurnResult,
    DialogTurnStatus,
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
    Activity,
    InputHints
)
# from botbuilder.azure import (
#     CosmosDbStorage,
#     CosmosDbConfig
# )
#
# from config import DefaultConfig
from domain.model import Delivery, DeliveryList
from resources import DeliveryCard, HelpCard


WF_DIALOG = "WFDialog"
DELIVERY = "delivery"

# CONFIG = DefaultConfig()
# COSMOS_DB_CONFIG = CosmosDbConfig(
#     endpoint=CONFIG.COSMOS_DB_SERVICE_ENDPOINT,
#     masterkey=CONFIG.COSMOS_DB_KEY,
#     database=CONFIG.COSMOS_DB_DATABASE_ID,
#     container=CONFIG.COSMOS_DB_CONTAINER_ID
# )


class DeliveryDialog(ComponentDialog):
    def __init__(
            self,
            user_state: UserState
    ):
        super(DeliveryDialog, self).__init__(DeliveryDialog.__name__)

        self.user_state = user_state
        self.did_show_entry_msg = False
        # self.storage = CosmosDbStorage(COSMOS_DB_CONFIG)
        self.storage = MemoryStorage()

        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))
        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(DateTimePrompt(DateTimePrompt.__name__))
        self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))
        self.add_dialog(
            WaterfallDialog(
                WF_DIALOG,
                [
                    self.intro_step,
                    self.action_step,
                    self.destination_step,
                    self.time_step,
                    self.confirm_step,
                    self.acknowledgement_step
                ],
            )
        )

        self.initial_dialog_id = WF_DIALOG

    async def intro_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        prompt_options = PromptOptions(
                prompt=MessageFactory.text(
                    "How may I help you?"
                ),
                choices=[
                    Choice("Create delivery"),
                    Choice("List deliveries"),
                    Choice("Exit")
                ]
            )
        return await step_context.prompt(ChoicePrompt.__name__, prompt_options)

    async def action_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        action = step_context.result.value.lower()

        if action == "create delivery":
            step_context.values[DELIVERY] = Delivery()
            delivery: Delivery = step_context.values[DELIVERY]
            delivery.item = step_context.result
            prompt_options = PromptOptions(
                prompt=MessageFactory.text(
                    "What would you like me to have delivered?"
                )
            )
            return await step_context.prompt(TextPrompt.__name__, prompt_options)

        elif action == "list deliveries":
            data = await self.storage.read(["DeliveryList"])
            delivery_list = data["DeliveryList"]["delivery_list"]
            print("delivery list: ", delivery_list)
            for delivery in delivery_list:
                DeliveryCard["body"][0]["text"] = delivery['item']
                DeliveryCard["body"][1]["text"] = delivery['destination']
                DeliveryCard["body"][2]["text"] = delivery['time']
                message = Activity(
                    type=ActivityTypes.message,
                    attachments=[
                        CardFactory.adaptive_card(DeliveryCard)
                    ],
                )
                await step_context.context.send_activity(message)
            return await step_context.end_dialog()

        elif action == "exit":
            await step_context.context.send_activity(MessageFactory.text("Goodbye!"))
            return await step_context.end_dialog()

    async def destination_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        delivery: Delivery = step_context.values[DELIVERY]
        delivery.destination = step_context.result

        prompt_options = PromptOptions(
            prompt=MessageFactory.text(
                "Where do you want this item delivered?"
            )
        )
        return await step_context.prompt(TextPrompt.__name__, prompt_options)

    async def time_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        delivery: Delivery = step_context.values[DELIVERY]
        delivery.time = step_context.result

        prompt_options = PromptOptions(
            prompt=MessageFactory.text(
                "When do you want this item delivered?"
            ),
            retry_prompt=MessageFactory.text(
                "Please enter a valid time"
            ),

        )
        return await step_context.prompt(DateTimePrompt.__name__, prompt_options)

    async def confirm_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        delivery: Delivery = step_context.values[DELIVERY]
        delivery.time = step_context.result[0].value
        prompt_options = PromptOptions(
            prompt=MessageFactory.text(
                f"""I have set the delivery. 
                \nIs there anything else I can help with?"""
            )
        )

        DeliveryCard["body"][0]["text"] = delivery.item
        DeliveryCard["body"][1]["text"] = delivery.destination
        DeliveryCard["body"][2]["text"] = delivery.time

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
        await self.create_delivery(step_context)
        if step_context.result:
            await step_context.context.send_activity(
                MessageFactory.text("okay")
            )
            return await step_context.begin_dialog(self.id)
        else:
            await step_context.context.send_activity(
                MessageFactory.text("Okay, goodbye!.")
            )
        return await step_context.end_dialog()

    async def on_continue_dialog(self, inner_dc: DialogContext) -> DialogTurnResult:
        result = await self.interrupt(inner_dc)
        if result is not None:
            return result
        return await super(DeliveryDialog, self).on_continue_dialog(inner_dc)

    async def interrupt(self, inner_dc: DialogContext) -> DialogTurnResult:
        if inner_dc.context.activity.type == ActivityTypes.message:
            text = inner_dc.context.activity.text.lower()
            message = Activity(
                type=ActivityTypes.message,
                attachments=[
                    CardFactory.adaptive_card(HelpCard)
                ])

            if text in ("help", "?"):
                await inner_dc.context.send_activity(message)
                return DialogTurnResult(DialogTurnStatus.Waiting)

            if text in ("cancel", "quit"):
                cancel_message_text = "Cancelled."
                cancel_message = MessageFactory.text(
                    cancel_message_text, cancel_message_text, InputHints.ignoring_input
                )
                await inner_dc.context.send_activity(cancel_message)
                return await inner_dc.cancel_all_dialogs()
        return None

    async def create_delivery(self, step_context):
        delivery: Delivery = step_context.values[Delivery]
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

