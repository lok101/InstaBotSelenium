from module.option import BotOption
import random


class Tools:
    @staticmethod
    def difference_sets(file_path):
        account_list, ignore_list = set(), set()
        Tools.file_read(file_path, account_list)
        Tools.file_read(BotOption.parameters['ignore_list_path'], ignore_list)
        account_list = account_list.difference(ignore_list)
        return account_list

    @staticmethod
    def file_read(file_path, value, operating_mode='r'):
        with open(f'data/{file_path}', operating_mode, encoding='utf-8') as file:
            if isinstance(value, set):
                for link in file:
                    value.add(link)
            elif isinstance(value, list):
                for link in file:
                    value.append(link)

    @staticmethod
    def file_write(file_path, value, operating_mode='a'):
        with open(f'data/{file_path}', operating_mode, encoding='utf-8') as file:
            if isinstance(value, (list, set)):
                for item in value:
                    if '\n' in item:
                        file.write(item)
                    else:
                        file.write(item + '\n')
            else:
                if '\n' in value:
                    file.write(str(value))
                else:
                    file.write(str(value) + '\n')

    @staticmethod
    def shaffle_file(file_path):
        file = []
        Tools.file_read(file_path, file)
        before = len(file)
        random.shuffle(file)
        Tools.file_write(file_path, file, operating_mode='w')
        file = []
        Tools.file_read(file_path, file)
        after = len(file)
        if before > after:
            raise Exception('Метод "shaffle_file" вернул меньше строк, чем получил.')
        elif before < after:
            raise Exception('Метод "shaffle_file" вернул больше строк, чем получил.')
