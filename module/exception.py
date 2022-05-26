from module.tools import Tools
from datetime import datetime


class BotException(BaseException):
    mode = None

    def __init__(self, account_option, message):
        self.account_option = account_option
        self.message = message
        self.date = datetime.now().strftime("%d-%m %H:%M:%S")
        self.time = datetime.now().strftime("%H:%M:%S")
        self.path = f'logs/Путь не присвоен.txt'
        self.log_text = 'Текст лога не присвоен.'

    def __str__(self):
        date = datetime.now().strftime("%d-%m %H:%M:%S")
        return f'\n{date} {BotException.mode}. {self.__class__.__name__} ----- {self.message}'

    def save_log_exception(self):
        Tools.file_write(self.path, self.log_text)


class BotCriticalException(BotException):
    def __init__(self, account_option, message):
        super(BotCriticalException, self).__init__(account_option, message)
        self.path = f'logs/{self.__class__.__name__}.txt'
        self.log_text = self.date + ' -- ' + self.account_option.account_data["user_name"].split("\n")[0] + ' -- ' + str(self.message)

    def __str__(self):
        return f'\n{self.date} {self.__class__.__name__} ----- {self.message}\n'


class LoginError(BotCriticalException):
    def __str__(self):
        self.save_log_exception()
        return self.log_text


class ActivBlocking(BotCriticalException):
    pass


class VerificationError(BotCriticalException):
    def __str__(self):
        self.save_log_exception()
        return self.log_text


class BotNonCriticalException(BotException):
    def __str__(self):
        return self.message


class UserPageNotExist(BotNonCriticalException):
    def __init__(self, account_option, message):
        super(UserPageNotExist, self).__init__(account_option, message)
        self.path = self.account_option.parameters["ignore_list_path"]
        self.log_text = self.account_option.user_url
        self.save_log_exception()


class PageLoadingError(BotNonCriticalException):
    pass


class PageNotAvailable(BotNonCriticalException):
    pass


class BotFinishTask(BotException):
    def __str__(self):
        return f'\n{self.time} <<{self.mode}>> {self.message}'


class FilteredOut(BotException):
    def __init__(self, account_option, message):
        super(FilteredOut, self).__init__(account_option, message)
        self.add_user_in_ignore_list()

    def __str__(self):
        self.add_user_in_filters_log()
        return self.message

    def add_user_in_ignore_list(self):
        self.path = self.account_option.parameters["ignore_list_path"]
        self.log_text = self.account_option.user_url
        self.save_log_exception()

    def add_user_in_filters_log(self):
        self.path = f'logs/{self.account_option.parameters["fil"]}/filter_out/{self.__class__.__name__}.txt'
        self.log_text = f'{self.date} {self.account_option.user_url} --- {self.message}'
        self.save_log_exception()


class StopWord(FilteredOut):
    pass


class BadProfile(FilteredOut):
    pass


class EmptyProfile(FilteredOut):
    def __str__(self):
        return self.message
