#!/usr/bin/env python
# -*- coding:utf-8 -*-

import yaml
from random import choice
from playhouse.db_url import connect

from automail.db import maildb
from automail.Template import Template
from automail.SwitchAccount import SwitchAccount
from automail.Mail import AutoMail
from automail.Gmail import AutoGmail


template = Template()


def read_yaml(yaml_path):
    with open(yaml_path, "r", encoding="utf-8") as config_file:
        config_data = yaml.safe_load(config_file.read())
    return config_data


def initialize(yaml_path="config.yaml"):
    config_data = read_yaml(yaml_path)
    mysql_url = "mysql://" + config_data["MySQL"]["user"] + ":" + config_data["MySQL"]["password"] + "@" + \
        str(config_data["MySQL"]["host"]) + ":" + str(config_data["MySQL"]["port"]) + "/" + config_data["MySQL"]["database"]
    print(mysql_url)
    database = connect(mysql_url)
    maildb.initialize_sql(database)
    maildb.xls2db(config_data["PATH"]["my_mail_account_excel"])
    maildb.txtmail2db(config_data["PATH"]["to_email_path"])
    maildb.toemail2local(config_data["PATH"]["to_email_path"])


def get_random_toemail(to_email_path):
    maildb.toemail2local(to_email_path)
    with open(to_email_path,"r",encoding="utf-8") as f:
        to_emails = f.readlines()
    return choice(to_emails)


def get_ramdom_template():
    templates = template.get_all_template()
    return choice(templates)


def get_random_account(mail_account:SwitchAccount):
    mail_accounts = mail_account.get_mail_accounts()
    account_temp = choice(mail_accounts)
    mail_account.mail_to_config(account_temp)
    return account_temp


def random_mail(mail_account:SwitchAccount,to_email_path):
    # 随机发件人
    random_account = get_random_account(mail_account)
    # print(random_account)
    randmon_mail = AutoMail(
        random_account[0],
        random_account[1],
        random_account[2],
        proxy="socks5://127.0.0.1:1080"
    )
    # 随机收件人随机模板
    randmon_mail.send_single(to_email=get_random_toemail(to_email_path), template_name=get_ramdom_template())


if __name__ == "__main__":
    initialize()
    # templates = Template().get_all_template()
    # print(templates)
    # a = SwitchAccount("data/mail_config.json")
    # print(a.get_current_email())
    # print(a.get_mail_accounts())

    # my_email = "automail1@163.com"
    # passwd = "abcd1234"
    # host = "smtp.163.com"
    # port = 465
    # # proxy = "socks5://127.0.0.1:1080"
    # auto_mail = AutoMail(my_email=my_email,passwd=passwd,host=host,port=465)
    # auto_mail.send_single(to_email="automail1@163.com", template_name = "233")

    # my_email = "churs.sam@gmail.com"
    # auto_mail = AutoGmail(my_email,oauth2_path="data/oauth2_creds.json", proxy="socks5://127.0.0.1:1080")
    # auto_mail.send_single(to_email="churs.sam@gmail.com", template_name = "template_custom", )


    my_email = "creatkim@163.com"
    passwd = "ds19991999"
    host = "smtp.163.com"
    port = 465
    # proxy = "socks5://127.0.0.1:1080"
    auto_mail = AutoMail(my_email=my_email,passwd=passwd,host=host,port=port)
    auto_mail.send_single(to_email="creatkim@163.com", template_name = "233")
