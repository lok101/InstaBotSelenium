from module.option import BotOption


class Tools:
    @staticmethod
    def difference_sets(file_path):
        account_list, ignore_list = set(), set()
        Tools.file_read(file_path, account_list)
        Tools.file_read(BotOption.parameters['ignore_list_path'], ignore_list)
        account_list = account_list.difference(ignore_list)
        return account_list

    @staticmethod
    def file_read(file_name, value, operating_mode='r'):
        with open(f'data/{file_name}', operating_mode, encoding='utf-8') as file:
            if isinstance(value, set):
                for link in file:
                    value.add(link)
            elif isinstance(value, list):
                for link in file:
                    value.append(link)

    @staticmethod
    def file_write(file_name, value, operating_mode='a'):
        with open(f'data/{file_name}', operating_mode, encoding='utf-8') as file:
            if isinstance(value, (list, set)):
                if '\n' in value.pop():
                    for item in value:
                        file.write(item)
                else:
                    for item in value:
                        file.write(item + '\n')
            else:
                if '\n' in value:
                    file.write(str(value))
                else:
                    file.write(str(value) + '\n')