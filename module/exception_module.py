from datetime import datetime


class BotException(BaseException):
    def __init__(self, message, mode):
        self.message = message
        self.mode = mode

    def __str__(self):
        time = datetime.now().strftime("%H:%M:%S")
        return f'\n{time} {self.mode}. {self.__class__.__name__} ----- {self.message}'


class BotCriticalException(BotException):
    pass


class LoginError(BotCriticalException):
    pass


class ActivBlocking(BotCriticalException):
    pass


class VerificationError(BotCriticalException):
    pass


class BotNotCriticalException(BotException):
    def __str__(self):
        return f'{self.message} '


class UserPageNotExist(BotNotCriticalException):
    pass


class PageLoadingError(BotNotCriticalException):
    pass


class BotFinishTask(BotException):
    def __str__(self):
        time = datetime.now().strftime("%H:%M:%S")
        return f'\n{time} <<{self.mode}>> {self.message}'


class FilterException(BaseException):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f'{self.message}'


class StopWordException(FilterException):
    def __init__(self, message, stop_word):
        super(StopWordException, self).__init__(message)
        self.stop_word = stop_word

    def __str__(self):
        return f'{self.message} Стоп-слово: {self.stop_word}'


class BadProfileException(FilterException):
    pass
