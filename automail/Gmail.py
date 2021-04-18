#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import yagmail
import json
import time

try:
	from Mail import AutoMail
	from ASMTP import SMTP
except Exception:
	from automail.Mail import AutoMail
	from automail.ASMTP import SMTP


class AutoGmail(AutoMail):
	"""
	特殊邮箱类：gmail的oauth2认证方式
	"""
	def __init__(self, my_email,oauth2_path, proxy=None, real_mail=["gmail.com", "hotmail.com", "outlook.com", "protonmail.com", "163.com"]):
		self.my_email = my_email
		self.oauth2_path = oauth2_path
		self.yag = SMTP(self.my_email, oauth2_file = self.oauth2_path)
		self.real_mail = real_mail
