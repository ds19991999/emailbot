#!/usr/bin/env python
# -*- coding:utf-8 -*-

import json
import os
from peewee import *
try:
    from db import maildb
except ImportError:
	from automail.db import maildb  


class Template(object):
    def __init__(self):
        pass

    def template_custom(self):
        """
        自定义邮件模板，保证所有的模板的名称不同
        """
        incorrect_name = True
        while incorrect_name:
            template_name = str(input("输入自定义邮件模板名称(默认template_custom)："))
            exist_name = maildb.check_tem(template_name)                
            if template_name is not None and not exist_name:
                incorrect_name = False
            else:
                print("模板名称已存在或输入错误！目前已有以下模板：")
                print(self.get_all_template())
        
        subject = str(input("邮件主题："))
        if subject == None:
            subject = "This is obviously the subject"
        contents_body = str(input("邮件正文："))
        if contents_body == None:
            contents_body = "This is obviously the body"
        contents_html = str(input("邮件HTML："))
        if contents_html == None:
            contents_html = ""
        contents_attachments = str(input("邮件附件："))
        if contents_attachments == None:
            contents_attachments == ""
        
        template_contents = {
            "subject":subject,
            "contents":[contents_body,contents_html,contents_attachments]
            }
        template = {
            "template_name": template_name,
            "template_contents": template_contents
        }
        maildb.tem2db(template)


    def get_all_template(self):
        """
        从数据库中获取所有模板名称
        """
        template_list = []
        templates = maildb.EmailTemplate.select(maildb.EmailTemplate.template_name).where(maildb.EmailTemplate.is_delete==False)
        for template in templates:
            template_list.append(template.template_name)
        return template_list


