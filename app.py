from aiohttp import web
from aiohttp.web import Request, Response
# from botbuilder.azure import CosmosDbStorage, CosmosDbConfig
from botbuilder.core import (
    BotFrameworkAdapterSettings,
    ConversationState,
    MemoryStorage,
    UserState
)
from botbuilder.schema import Activity

from adapters import ErrorAdapter
from bots import DeliveryBot
from config import DefaultConfig
from dialogs import MainDialog

CONFIG = DefaultConfig()

SETTINGS = BotFrameworkAdapterSettings(CONFIG.APP_ID, CONFIG.APP_PASSWORD)

# Create MemoryStorage, UserState and ConversationState
# COSMOS_DB_CONFIG = CosmosDbConfig(
#     endpoint=CONFIG.COSMOS_DB_SERVICE_ENDPOINT,
#     masterkey=CONFIG.COSMOS_DB_KEY,
#     database=CONFIG.COSMOS_DB_DATABASE_ID,
#     container=CONFIG.COSMOS_DB_CONTAINER_ID
# )
# MEMORY = CosmosDbStorage(COSMOS_DB_CONFIG)
MEMORY = MemoryStorage()
USER_STATE = UserState(MEMORY)
CONVERSATION_STATE = ConversationState(MEMORY)

# Create adapter.
# See https://aka.ms/about-bot-adapter to learn more about how bots work.
ERROR_ADAPTER = ErrorAdapter(SETTINGS, CONVERSATION_STATE)

# Create dialogs and Bot
DIALOG = MainDialog(USER_STATE, MEMORY)
BOT = DeliveryBot(CONVERSATION_STATE, DIALOG, USER_STATE)

AUTHORIZATION_HEADER = "Authorization"
CONTENT_TYPE_HEADER = "Content-Type"
JSON_CONTENT_TYPE = "application/json"


# Listen for incoming requests on /api/messages
async def messages(req: Request) -> Response:
    # Main bot message handler.
    if JSON_CONTENT_TYPE in req.headers[CONTENT_TYPE_HEADER]:
        body = await req.json()
    else:
        return Response(status=415)

    activity = Activity().deserialize(body)
    auth_header = req.headers[AUTHORIZATION_HEADER] if AUTHORIZATION_HEADER in req.headers else ""

    try:
        await ERROR_ADAPTER.process_activity(activity, auth_header, BOT.on_turn)
        return Response(status=201)
    except Exception as exception:
        raise exception


APP = web.Application()
APP.router.add_post("/api/messages", messages)

if __name__ == "__main__":
    try:
        web.run_app(APP, host=CONFIG.HOST, port=CONFIG.PORT)
    except Exception as error:
        raise error
