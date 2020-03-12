from botbuilder.core import ActivityHandler, MessageFactory, TurnContext
from botbuilder.schema import Activity, ActivityTypes, EndOfConversationCodes


END_TEXT = "end"
EXIT_TEXT = "exit"


class EchoBot(ActivityHandler):
    """ EchoBot activity handler"""

    async def on_message_activity(self, turn_context: TurnContext):
        activity_text: str = turn_context.activity.text
        if EXIT_TEXT in activity_text or END_TEXT in activity_text:
            # Send End of conversation at the end.
            await turn_context.send_activity(
                MessageFactory.text("Ending conversation from the skill...")
            )

            end_of_conversation = Activity(type=ActivityTypes.end_of_conversation)
            end_of_conversation.code = EndOfConversationCodes.completed_successfully
            await turn_context.send_activity(end_of_conversation)
        else:
            await turn_context.send_activity(
                MessageFactory.text(f"You said: {activity_text}")
            )
            await turn_context.send_activity(
                MessageFactory.text(
                    f'Say {END_TEXT} or {EXIT_TEXT} and I\'ll end the conversation.'
                )
            )
