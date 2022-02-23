class BotException(Exception):
    pass


class LoginError(BotException):
    pass


class ActivBlocking(BotException):
    pass


class VerificationError(BotException):
    pass
