from datetime import datetime

import peewee
from peewee import *

db = SqliteDatabase('data/accounts.db')


class DataBase(Model):
    account_id = PrimaryKeyField()
    date = DateTimeField(default=datetime.now().strftime('%d-%m-%Y %H:%M:%S'))
    date_verification = DateTimeField(default=datetime.now().strftime('%d-%m-%Y %H:%M:%S'))
    account_status = CharField()
    user_name = CharField()
    user_pass = CharField()
    email_name = CharField()
    email_pass = CharField()
    email_codeword = CharField()
    cookie = CharField(null=True)
    user_agent = CharField(null=True)

    class Meta:
        database = db


def create_entry_db(user_name, user_pass, email_name, email_pass, email_codeword, account_status='bot'):
    try:
        DataBase.create_table()
        DataBase.create(user_name=user_name,
                        user_pass=user_pass,
                        email_name=email_name,
                        email_pass=email_pass,
                        email_codeword=email_codeword,
                        account_status=account_status)

    except peewee.IntegrityError as ex:
        print(ex)


def get_account_field_data(account_id):
    return_dict = dict()
    entry = DataBase.get(DataBase.account_id == account_id)
    return_dict['account_id'] = entry.account_id
    return_dict['user_name'] = entry.user_name
    return_dict['user_pass'] = entry.user_pass
    return_dict['email_name'] = entry.email_name
    return_dict['email_pass'] = entry.email_pass
    return_dict['email_codeword'] = entry.email_codeword
    return_dict['user_agent'] = entry.user_agent
    return return_dict


def get_accounts_id_on_status(account_status):
    return_list = list()
    for entry in DataBase.select():
        if entry.account_status == account_status:
            return_list.append(entry.account_id)
    return return_list


def delete_entry(account_id):
    entry = DataBase.get(DataBase.account_id == account_id)
    entry.delete_instance()
