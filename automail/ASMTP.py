#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
代理池：
https://github.com/jhao104/proxy_pool
"""

import os
import json
import smtplib
import socks
import yagmail

from yagmail.message import prepare_message
from yagmail.headers import resolve_addresses
from yagmail.validate import validate_email_with_regex

from urllib import request
from urllib.error import URLError

from yagmail import SMTP as YSMTP

class SMTP(YSMTP):
    """
    重写yagmail.SMTP, 增加代理
    """
    def __init__(
        self,
        user=None,
        password=None,
        host="smtp.gmail.com",
        port=None,
        smtp_starttls=None,
        smtp_ssl=True,
        smtp_set_debuglevel=0,
        smtp_skip_login=False,
        encoding="utf-8",
        oauth2_file=None,
        soft_email_validation=True,
        proxy = None, # eg: "socks5://127.0.0.1:1080"
        **kwargs
    ):
        super().__init__(
            user,
            password,
            host,
            port,
            smtp_starttls,
            smtp_ssl,
            smtp_set_debuglevel,
            smtp_skip_login,
            encoding,
            oauth2_file,
            soft_email_validation,
            **kwargs
        )

        self.proxy = proxy

        if proxy == None:
            pass
        else:
            self.set_proxy()
 
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
        socks.wrapmodule(smtplib)
    
    def test_proxy(self):
        """
        测试代理
        """
        try:
            response = request.urlopen('http://httpbin.org/get')
            print(response.read().decode('utf-8'))
        except URLError as e:
            print(e.reason)
    
    def prepare_send(
        self,
        fake_mail,
        fake_name,
        to=None,
        subject=None,
        contents=None,
        attachments=None,
        cc=None,
        bcc=None,
        headers=None,
        newline_to_break=True,
    ):
        addresses = resolve_addresses(self.user, self.useralias, to, cc, bcc)

        if self.soft_email_validation:
            for email_addr in addresses["recipients"]:
                validate_email_with_regex(email_addr)

        msg = prepare_message(
            fake_mail, #self.user,              # 发信人地址
            fake_name, #self.useralias,         # 隐藏用户别名
            addresses,                          # 收信人地址
            subject,
            contents,
            attachments,
            headers,
            self.encoding,
            newline_to_break,
        )

        recipients = addresses["recipients"]
        msg_string = msg.as_string()
        return recipients, msg_string

    def send(
        self,
        fake_mail=None,
        fake_name=None,
        to=None,
        subject=None,
        contents=None,
        attachments=None,
        cc=None,
        bcc=None,
        preview_only=False,
        headers=None,
        newline_to_break=True,
    ):
        """ Use this to send an email with gmail"""
        fake_mail = self.user if fake_mail == None else fake_mail
        fake_name = self.useralias if fake_name == None else fake_name

        self.login()
        recipients, msg_string = self.prepare_send(
            fake_mail, fake_name, to, subject, contents, attachments, cc, bcc, headers, newline_to_break
        )
        if preview_only:
            return (recipients, msg_string)
        return self._attempt_send(recipients, msg_string)


def main():
    yag = SMTP(user="churs.sam@gmail.com",  password="bVF3T1ZKUVZE", host="smtp.gmail.com",proxy="socks5://127.0.0.1:1080")
    yag.send(to="sdw3dw@protonmail.com", subject="匿名邮件测试", contents="yagmail 代理测试", fake_mail="admin@qq.com",fake_name="admin")


if __name__ == "__main__":
    main()

