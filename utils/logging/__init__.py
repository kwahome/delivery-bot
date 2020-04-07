import logging


LOGGER = logging.getLogger(__name__)
HANDLER = logging.StreamHandler()
FORMATTER = logging.Formatter(
    "%(asctime)s [%(levelname)s %(filename)s.%(funcName)s:L%(lineno)s]: %(message)s"
)
HANDLER.setFormatter(FORMATTER)
if not LOGGER.handlers:
    LOGGER.addHandler(HANDLER)
LOGGER.setLevel("DEBUG")
