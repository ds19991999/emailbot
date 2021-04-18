#!/usr/bin/env python
# -*- coding:utf-8 -*-

import imaplib
import email
import json
import socks
import os

try:
    from POP3 import decode_mail
except Exception:
    from automail.POP3 import decode_mail


class AIMAP(object):
    def __init__(self,username,password,server,port,proxy=None):
        self.username = username
        self.password = password
        self.server = server
        self.port = port
        self.proxy = proxy
        if proxy == None:
            pass
        else:
            self.set_proxy()

    def login(self):
        self.mail = imaplib.IMAP4_SSL(self.server, self.port)
        self.mail.login(self.username,self.password)

    def set_proxy(self):
        """
        设置代理
        """
        proxy_list = self.proxy.replace('/', '').split(":")
        proxy_type = str(proxy_list[0])
        proxy_host = str(proxy_list[1])
        proxy_port = int(proxy_list[2])
    
        if proxy_type == "socks4":
            SOCKS = socks.SOCKS4
        elif proxy_type == "socks5":
            SOCKS = socks.SOCKS5
        elif proxy_type == "http":
            SOCKS = socks.HTTP
        socks.setdefaultproxy(proxy_type=SOCKS, addr=proxy_host, port=proxy_port, username=None, password=None)
        socks.wrapmodule(imaplib)

    def mail_inbox_latest_one(self):
        """获取收件箱最新邮件"""
        self.mail.select("inbox")
        result, data = self.mail.uid('search', None, "ALL")
        latest_email_uid = data[0].split()[-1]

        result, data = self.mail.uid('fetch', latest_email_uid, '(RFC822)')
        raw_email = data[0][1]
        return decode_mail(raw_email)

    def mail_box(self,box="inbox"):
        """
        获取收件箱所有邮件
        box: "inbox", "all", "send"
        """
        try:
            self.mail.select(box)
        except Exception:
            print("该邮件类型没有此邮件文件夹！")

        result, data = self.mail.uid('search', None, "ALL")
        uid_list = data[0].split()

        for uid in uid_list:
            result, data = self.mail.uid('fetch', uid, '(RFC822)')
            raw_email = data[0][1]
            yield decode_mail(raw_email)

