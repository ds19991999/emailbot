#!/usr/bin/env python
# -*- coding:utf-8 -*-

import poplib
import email
import json
import socks
import os


def decode_header(header):
    decoded_bytes, charset = email.header.decode_header(header)[0]
    if charset is None:
        return str(decoded_bytes)
    else:
        return decoded_bytes.decode(charset)


def decode_mail(raw_email):
    email_text = {}
    text_list = []
    attachment_list = []
    unknown_list = []
    parsed_email = email.message_from_bytes(raw_email)

    email_text["from"] = parsed_email['From']
    email_text["to"] = parsed_email['To']
    email_text["date"] = parsed_email['Date']
    email_text["subject"] = decode_header(parsed_email['Subject'])

    for part in parsed_email.walk():
        if part.is_multipart():
            # maybe need also parse all subparts
            continue
        elif part.get_content_maintype() == 'text':
            text = part.get_payload(decode=True).decode(part.get_content_charset())
            text_list.append(text)
        elif part.get_content_maintype() == 'application' and part.get_content_disposition() == 'attachment':
            name = decode_header(part.get_filename())
            body = part.get_payload(decode=True)
            size = len(body)
            attachment_text = '"{}", size: {} bytes, starts with: "{}"'.format(name, size, body[:50])
            attachment_list.append(attachment_text)
        else:
            unknown_list.append(part.get_content_type())
        email_text["text"] = text_list
        email_text["attachment"] = attachment_list
        email_text["unknown"] = unknown_list
        return email_text   


class APOP(object):
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
        self.mail = poplib.POP3_SSL(self.server, self.port)
        self.mail.user(self.username)
        self.mail.pass_(self.password)
    
    def message(self):
        self.num_mail = len(self.mail.list()[1])
        for i in range(self.num_mail):
            raw_email  = b"\n".join(self.mail.retr(i+1)[1])
            email_temp = decode_mail(raw_email)
            print('======== email #%i ended =========' % i)
            yield email_temp

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
        socks.wrapmodule(poplib)

