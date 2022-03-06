class BotCriticalException(BaseException):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f'{self.__class__.__name__} ----- {self.message} '


class LoginError(BotCriticalException):
    pass


class ActivBlocking(BotCriticalException):
    pass


class VerificationError(BotCriticalException):
    pass


class BotException(BaseException):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f'{self.__class__.__name__} ----- {self.message} '


class UserPageNotExist(BotException):
    pass


class PageLoadingError(BotException):
    pass


class FilterException(BaseException):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f'{self.__class__.__name__} ----- {self.message} '


class StopWordException(FilterException):
    def __init__(self, message, stop_word):
        super(StopWordException, self).__init__(message)
        self.stop_word = stop_word

    def __str__(self):
        return f'{self.__class__.__name__} ----- {self.message}. Стоп-слово: {self.stop_word} '


class BadProfileException(FilterException):
    pass
