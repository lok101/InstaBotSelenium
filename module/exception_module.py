from module.message_text_module import FilterMessage
from module.base_module import BaseClass
from settings import StartSettings
from datetime import datetime
import traceback
import time


class ExceptionHandling:
    def __init__(self, account_option):
        self.account_option = account_option

    def standard_exception_handling(self):

        self.save_log_exception()
        exception_name = str(type(self.account_option.exception)).split("'")[1].split('.')[-1]
        if self.account_option.mode == self.account_option.parameters['fil'] and isinstance(self.account_option.exception, KeyError):
            raise BotFinishTask(FilterMessage.list_empty)
        print(f'\nЛог: {self.account_option.mode}/{exception_name} -- {self.account_option.exception}')

    def catching_critical_bot_exceptions(self):

        if isinstance(self.account_option.exception, (VerificationError, LoginError)):
            exception_name = str(type(self.account_option.exception)).split("'")[1].split('.')[-1]
            path = f'logs/{exception_name}.txt'
            message = self.account_option.username.split("\n")[0] + ' ----- ' + str(self.account_option.exception)
            BaseClass.file_write(path, message)

        elif isinstance(self.account_option.exception, ActivBlocking):
            pass

        print(f'{self.account_option.exception}')

    def catching_non_critical_bot_exceptions(self):

        if isinstance(self.account_option.exception, UserPageNotExist):
            BaseClass.file_write((self.account_option.parameters["ignore_list_path"]), BaseClass.user_url)

        elif isinstance(self.account_option.exception, (PageLoadingError, PageNotAvailable)):
            pass

        print(f'{self.account_option.exception}')

    def bot_filter_out_handling(self, user_url):

        if not isinstance(self.account_option.exception, EmptyProfile):
            exception_name = str(type(self.account_option.exception)).split("'")[1].split('.')[-1]
            path = f'logs/{self.account_option.parameters["fil"]}/filter_out/{exception_name}.txt'
            message = str(user_url.split("\n")[0]) + ' ----- ' + str(self.account_option.exception)
            BaseClass.file_write(path, message)

        BaseClass.file_write((self.account_option.parameters["ignore_list_path"]), user_url)
        print(f'{self.account_option.exception}')

    def save_log_exception(self):
        exception_name = str(type(self.account_option.exception)).split("'")[1].split('.')[-1]
        path = f'logs/{self.account_option.mode}/{exception_name}.txt'

        date = datetime.now().strftime("%d-%m %H:%M:%S")
        exception_text = traceback.format_exc()
        message = f'{date}\n{exception_text}\n\n'

        BaseClass.file_write(path, message)

        if 'CONNECTION_FAILED' in exception_text:
            timeout = StartSettings.err_proxy_timeout
            error_name = exception_text.split('net::')[1].split('\n')[0]
            print(f'{date.split(" ")[1]} -- {self.account_option.mode} >> {error_name}. ',
                  f'Запись добавлена в лог. Таймаут {timeout} секунд.')
            time.sleep(timeout)


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
        time = datetime.now().strftime("%H:%M:%S")
        return f'\n{time} <<{self.mode}>> {self.message}'


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
