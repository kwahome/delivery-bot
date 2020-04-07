from datetime import datetime

from botbuilder.core import (
    BotFrameworkAdapter,
    BotFrameworkAdapterSettings,
    ConversationState,
    TurnContext,
)
from botbuilder.schema import ActivityTypes, Activity

from resources import messages
from utils.logging import LOGGER


class ErrorAdapter(BotFrameworkAdapter):

    def __init__(
        self,
        settings: BotFrameworkAdapterSettings,
        conversation_state: ConversationState,
    ):
        super().__init__(settings)
        self._conversation_state = conversation_state

        # Catch-all for errors.
        async def on_error(context: TurnContext, error: Exception):
            # This check writes out errors to console log
            # NOTE: In production environment, you should consider logging this to Azure
            #       application insights.
            LOGGER.error(
                msg=f"An unhandled error has occurred: '{error.__class__.__name__}: {str(error)}'"
            )

            # Send a message to the user
            await context.send_activity(messages.SOMETHING_WENT_WRONG)

            # Send a trace activity if we're talking to the Bot Framework Emulator
            if context.activity.channel_id == "emulator":
                # Create a trace activity that contains the error object
                trace_activity = Activity(
                    label="TurnError",
                    name="on_turn_error Trace",
                    timestamp=datetime.utcnow(),
                    type=ActivityTypes.trace,
                    value=f"{error}",
                    value_type="https://www.botframework.com/schemas/error",
                )
                # Send a trace activity, which will be displayed in Bot Framework Emulator
                await context.send_activity(trace_activity)

            # Clear out state
            nonlocal self
            await self._conversation_state.delete(context)

        self.on_turn_error = on_error
