#!/usr/bin/env python
# -*- coding:utf-8 -*-

import xlrd
import re
import json
import os
import datetime

from peewee import *
import warnings
warnings.filterwarnings('ignore')


database_proxy = Proxy()


class BaseModel(Model):
    class Meta:
        database = database_proxy


class EmailAccount(BaseModel):
    account_id = AutoField(primary_key=True)
    email = CharField(index=True)
    passwd = CharField(index=True)
    host = CharField()
    create_time = DateTimeField(default=datetime.datetime.now)
    send_times = IntegerField(default=0)
    is_valid = BooleanField(default=True)
    is_delete = BooleanField(default=False)
    class Meta:
        table_name = "email_account"  # 自定义表名


class SendEmail(BaseModel):
    send_id = AutoField(primary_key=True)
    my_email = CharField()
    to_email = CharField()
    template_name = CharField()
    create_time = DateTimeField(default=datetime.datetime.now)
    is_delete = BooleanField(default=False)
    class Meta:
        table_name = "send_email"  # 自定义表名


class EmailTemplate(BaseModel):
    template_id = AutoField(primary_key=True)
    template_name = CharField(index=True)
    template_contents = TextField()
    send_times = IntegerField(default=0)
    create_time = DateTimeField(default=datetime.datetime.now)
    is_delete = BooleanField(default=False)
    class Meta:
        table_name = "email_template"  # 自定义表名


class ToEmail(BaseModel):
    email_id = AutoField(primary_key=True)
    to_email = CharField(index=True)
    send_times = IntegerField(default=0)
    create_time = DateTimeField(default=datetime.datetime.now)
    is_delete = BooleanField(default=False)
    class Meta:
        table_name = "to_email"  # 自定义表名


class ExcelProcess(object):
    def __init__(self, mail_account_path):
        self.mail_account_path = mail_account_path
    
    def read_excel(self):
        workspace = xlrd.open_workbook(filename=self.mail_account_path)
        # 通过索引获取第一个表格
        sheet = workspace.sheet_by_index(0)
        # 获取行内容
        nrows = sheet.nrows
        line_list = []
        for nrow in range(nrows):
            line_list.append(sheet.row_values(nrow))
        return line_list


def initialize_sql(database):
    database_proxy.initialize(database)
    database_proxy.create_tables([EmailAccount, SendEmail, EmailTemplate, ToEmail])


def check_tem(tem_name):
    """
    查询模板名是否存在
    """
    sql = EmailTemplate.select(
        EmailTemplate.template_name,
        EmailTemplate.template_contents
        ).where(EmailTemplate.is_delete == False)
    template = sql.get()
    try:
        template = sql.get()
    except EmailTemplate.DoesNotExist:
        template = None
    return template


def check_email(email,passwd):
    """
    查询邮箱账号是否存在email_account表中
    """
    sql = EmailAccount.select(
        EmailAccount.email,
        EmailAccount.passwd
    ).where(
        EmailAccount.email==email,
        EmailAccount.passwd==passwd
        )
    try:
        email_account = sql.get()
    except EmailAccount.DoesNotExist:
        email_account = None
    return email_account


def check_to_email(email):
    """
    查询邮箱是否存在to_email表中
    """
    sql = ToEmail.select(
        ToEmail.to_email
    ).where(ToEmail.to_email==email)
    try:
        to_email = sql.get()
    except ToEmail.DoesNotExist:
        to_email = None
    return to_email


def txtmail2db(to_email_path):
    """
    将to_email导入数据库
    """
    with open(to_email_path, "r", encoding="utf-8") as f:
        email_temp_list = f.readlines()
    if len(email_temp_list) <= 0:
        print("[----] 导入异常！")
        os.system("exit")
    email_temp_list = list(set(email_temp_list))
    flag = False
    for email in email_temp_list:
        email = email.strip()
        pattern =r"^[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}$"
        if re.match(pattern, email):
            if not check_to_email(email):
                flag = True
                ToEmail.create(to_email=email)
    if flag:
        print("[++++] 成功将需要发送邮件的账号导入 to_email 表中！")
    else:
        print("[----] 文件 %s 中没有新的邮箱数据！" % to_email_path)


def xls2db(excel_path):
    """
    将密码账号的excel表格导入email_template表
    """
    email_accounts = ExcelProcess(excel_path).read_excel()
    if email_accounts:
        flag = False
        for email in email_accounts:
            pattern =r"^[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}$"
            # 如果是邮箱并且数据库中不存在或者数据库中已经删除
            if re.match(pattern,email[0]):
                if not check_email(email[0], email[1]):
                    flag = True
                    EmailAccount.create(
                        email=email[0],
                        passwd=email[1],
                        host=email[2]
                    )
        if flag:
            print("[++++] 成功将 %s 导入数据库中！" % excel_path)
        else:
            print("[----] 表格 %s 没有新的数据！" % excel_path)
        
    
def tem2db(template:dict):
    """
    将模板文件内容导入email_template表
    """
    # with open(template_path, "r",encoding = "utf-8") as f:
    #     template_contents = json.loads(f.read())
    # template_contents = str(template_contents)
    # template_name = os.path.splitext(os.path.split(template_path)[1])[0]
    template_name = template["template_name"]
    template_contents = template["template_contents"]
    if not check_tem(template_name):
        EmailTemplate.create(
            template_name = template_name,
            template_contents = template_contents
        )
        print("[++++] 成功将模板 %s 导入数据库中！" % template_name)
    else:
        print("[----] 模板 %s 已存在！" % template_name)


def send2db(my_email,to_email,tem_name):
    """
    将已发送的邮件信息保存到数据库
    """
    try:
        SendEmail.create(
            my_email = my_email,
            to_email = to_email,
            template_name = tem_name
        )
        print("[++++] 成功将邮件 %s 导入数据库中！" % tem_name)
    except Exception:
        print("[----] 无法将邮件 %s 导入数据库中！" % tem_name)


def toemail2local(to_email_path):
    """
    将数据库所有要发送的邮箱保存到本地
    """
    try:
        emails = ToEmail.select(
            ToEmail.to_email
            ).where(ToEmail.is_delete==False)
        with open(to_email_path, "w", encoding="utf-8") as f:
            for email in emails:
                f.write(email.to_email+"\n")
        print("[++++] 发送邮箱账号成功导出到本地 %s ！" % to_email_path)
    except Exception:
        print("[----] 发送账号导出异常！")


def to_email_counts(to_email):
    """
    to_email 发送邮件计数
    """
    sql = ToEmail.select(
        ToEmail.to_email,
        ToEmail.send_times
    ).where(
        ToEmail.to_email==to_email,
        ToEmail.is_delete==False
        )
    try:
        email_obj = sql.get()
    except ToEmail.DoesNotExist:
        email_obj = None
    if not email_obj:
        ToEmail.create(
            to_email = to_email
        )
    else:
        send_times = email_obj.send_times + 1
        print(send_times)
        ToEmail.update(send_times=send_times).where(
            ToEmail.to_email==to_email,
            ToEmail.is_delete==False
        ).execute()


def my_email_counts(my_email):
    """
    my_email 发送邮件计数
    """
    sql = EmailAccount.select(
        EmailAccount.email, 
        EmailAccount.send_times
    ).where(
        EmailAccount.email==my_email,
        EmailAccount.is_delete==False
    )
    try:
        email_obj = sql.get()
    except EmailAccount.DoesNotExist:
        email_obj = None
    if email_obj:
        send_times = email_obj.send_times + 1
        EmailAccount.update(send_times=send_times).where(
            EmailAccount.email == my_email,
            EmailAccount.is_delete==False
        ).execute()


def template_counts(email_template):
    """
    template模板邮件计数
    """
    sql = EmailTemplate.select(
        EmailTemplate.template_name,
        EmailTemplate.send_times
    ).where(
        EmailTemplate.template_name==email_template,
        EmailTemplate.is_delete==False
    )
    try:
        template_obj = sql.get()
    except EmailTemplate.DoesNotExist:
        template_obj = None
    if template_obj:
        send_times = template_obj.send_times + 1
        EmailTemplate.update(send_times=send_times).where(
            EmailTemplate.template_name==email_template,
            EmailTemplate.is_delete==False
        ).execute()
