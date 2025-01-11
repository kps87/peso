import logging


def title():
    print("_____________________ _________________   ")
    print("\\______   \\_   _____//   _____/\\_____  \\  ")
    print(" |     ___/|    __)_ \\_____  \\  /   |   \\ ")
    print(" |    |    |        \\/        \\/    |    \\")
    print(" |____|   /_______  /_______  /\\_______  /")
    print("                  \\/        \\/         \\/ ")


class Log:
    def __init__(self):
        pass

    @classmethod
    def get_logger(cls, name) -> logging.Logger:
        # Create a logger
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)

        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Create formatter and add it to the handler
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(formatter)

        # Add the handler to the logger
        logger.addHandler(console_handler)

        return logger
