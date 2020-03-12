import os


class DefaultConfig:
    """ Bot Configuration """

    HOST = "0.0.0.0"
    PORT = 3978
    APP_ID = os.environ.get("MICROSOFT_APP_ID", "")
    APP_PASSWORD = os.environ.get("MICROSOFT_APP_PASSWORD", "")
    CONNECTION_NAME = "echo-bot"
