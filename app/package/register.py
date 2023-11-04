import logging
import os.path
from logging.handlers import TimedRotatingFileHandler


class LogMaker:
    """
    Write log files with three levels:

    DEBUG: Detailed information, typically useful only for diagnosing problems.
    INFO: Confirmation that things are working as expected.
    WARNING: An indication that something unexpected happened, or indicative of some problem in the near future. The software is still functioning as expected.
    ERROR: Due to a more serious problem, the software has not been able to perform some function.
    CRITICAL: A very serious error, indicating that the program itself may be unable to continue running.
    """
    path = "codesmell_hunter.log"
    handler = TimedRotatingFileHandler(path, when="midnight", backupCount=1)
    handler.suffix = "%Y-%m-%d"
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", handlers=[handler]
    )

    @staticmethod
    def write_log(message: str, level: str) -> None:
        print(message)
        match level.lower():
            case "info":
                logging.info(message)
            case "debug":
                logging.debug(message)
            case "warning":
                logging.warning(message)
            case "error":
                logging.error(message)
