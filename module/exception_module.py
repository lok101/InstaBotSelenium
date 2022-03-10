from datetime import datetime


class BotException(BaseException):
    mode = None

    def __init__(self, message):
        self.message = message

    def __str__(self):
        date = datetime.now().strftime("%d-%m %H:%M:%S")
        return f'\n{date} {BotException.mode}. {self.__class__.__name__} ----- {self.message}'


class BotCriticalException(BotException):
    def __str__(self):
        date = datetime.now().strftime("%d-%m %H:%M:%S")
        return f'\n{date} {self.__class__.__name__} ----- {self.message}'


class LoginError(BotCriticalException):
    pass


class ActivBlocking(BotCriticalException):
    pass


class VerificationError(BotCriticalException):
    def __str__(self):
        date = datetime.now().strftime("%d-%m %H:%M:%S")
        return f'\n{date} ----- {self.message}'


class BotNonCriticalException(BotException):
    def __str__(self):
        return f'{self.message} '


class UserPageNotExist(BotNonCriticalException):
    pass


class PageLoadingError(BotNonCriticalException):
    pass


class PageNotAvailable(BotNonCriticalException):
    pass


class BotFinishTask(BotException):
    def __str__(self):
        date = datetime.now().strftime("%H:%M:%S")
        return f'\n{date} <<{self.mode}>> {self.message}'


class FilteredOut(BaseException):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f'{self.message}'


class StopWord(FilteredOut):
    def __init__(self, message, stop_word):
        super(StopWord, self).__init__(message)
        self.stop_word = stop_word

    def __str__(self):
        return f'{self.message} {self.stop_word}'


class BadProfile(FilteredOut):
    pass


class EmptyProfile(FilteredOut):
    pass
