import os


class DefaultConfig:
    """ Bot Configuration """

    HOST = "0.0.0.0"
    PORT = 3978

    CONNECTION_NAME = os.environ.get("CONNECTION_NAME", "echo-bot")
    APP_ID = os.environ.get("MICROSOFT_APP_ID", "")
    APP_PASSWORD = os.environ.get("MICROSOFT_APP_PASSWORD", "")

    LUIS_APP_ID = os.environ.get("LUIS_APP_ID", "")
    LUIS_API_KEY = os.environ.get("LUIS_API_KEY", "")
    # LUIS endpoint host name, ie "westus.api.cognitive.microsoft.com"
    LUIS_API_HOST_NAME = os.environ.get("LUIS_API_HOST_NAME", "westus.api.cognitive.microsoft.com")
