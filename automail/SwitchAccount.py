#!/usr/bin/env python
# -*- coding:utf-8 -*-

import json
try:
    from db import maildb
except Exception:
	from automail.db import maildb  


class SwitchAccount(object):
    def __init__(self, mail_config_path):
        self.mail_config_path = mail_config_path

    def get_current_email(self):
        """
        获取当前邮箱账号
        """
        with open(self.mail_config_path,"r",encoding="utf-8") as f:
            current_email = json.loads(f.read())
        return current_email

    def get_mail_accounts(self):
        """
        从数据库中获取所有邮箱账号
        """
        email_account_list = []
        sql = maildb.EmailAccount.select(
            maildb.EmailAccount.email,
            maildb.EmailAccount.passwd,
            maildb.EmailAccount.host
        ).where(maildb.EmailAccount.is_delete==False)
        email_accounts = sql.execute()
        for  email_account_obj in  email_accounts:
            email_account = {
                "email": email_account_obj.email,
                "passwd": email_account_obj.passwd,
                "host": email_account_obj.host
            }
            email_account_list.append(email_account)
        return email_account_list


    def mail_to_config(self,mail_account):
        """
        将单个邮箱账号写入邮箱配置文件
        """
        mail_config = {}
        mail_config["my_email"] = mail_account[0]
        mail_config["passwd"] = mail_account[1]
        mail_config["host"] = mail_account[2]
        with open(self.mail_config_path,"w",encoding="utf-8") as f:
            f.write(json.dumps(mail_config, indent=4, ensure_ascii=False))

