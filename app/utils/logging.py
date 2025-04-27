import datetime

class Logger:
    LEVELS = {
        "INFO": "INFO",
        "DEBUG": "DEBUG",
        "ERROR": "ERROR"
    }

    def __init__(self, name="Logger"):
        self.name = name

    def _log(self, level: str, message: str):
        if level in self.LEVELS:
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"[{timestamp}] [{self.name}] [{level}] {message}")
        else:
            self._log("ERROR", "invalid log level, choose from [INFO, DEBUG, ERROR]")

    def info(self, message):
        self._log("INFO", message)

    def debug(self, message):
        self._log("DEBUG", message)

    def error(self, message):
        self._log("ERROR", message)

logger = Logger(name="TravelApp")
