#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import yagmail
import json
import time
import re
import smtplib

try:
	from DB import maildb
	from ASMTP import SMTP
	from Template import Template
	from SwitchAccount import SwitchAccount
except ImportError:
	from automail.db import maildb
	from automail.ASMTP import SMTP
	from automail.Template import Template
	from automail.SwitchAccount import SwitchAccount


class AutoMail(object):
	def __init__(self,my_email,passwd,host,port=None,proxy=None, real_mail=["gmail.com", "hotmail.com", "outlook.com", "protonmail.com", "163.com"]):
		"""
		初始化
		"""
		self.my_email = my_email
		self.passwd = passwd
		self.host = host
		self.port = port
		self.proxy = proxy
		self.yag = SMTP(
			user = self.my_email, 
			password = self.passwd,
			host=self.host,
			port=self.port, 
			proxy=self.proxy
			)
		self.real_mail = real_mail
	
	def send_test(self, to_email="churs.sam@gmail.com"):
		"""
		发送邮件测试
		"""
		contents = "这里是内容"
		subject = "主题"
		
		t0 = time.perf_counter()
		result = self.yag.send(to=to_email,contents=contents, subject=subject)
		t1 = time.perf_counter()
		time_long = t1-t0

		# 将发送的邮件保存到数据库
		maildb.send2db(self.my_email, to_email, tem_name="send_test")
		self.send_result(result,time_long)
	
	def send_result(self,result,time_long):
		"""
		邮件发送结果
		"""
		if result == {}:
			print("Send email success! Spend time %ss." % time_long)
		else:
			print("Send Error! Spend time %ss." % time_long)

	def send_single(self, to_email="churs.sam@gmail.com", template_name = "template_default"):
		"""
		发送单个邮件
		"""
		template = maildb.check_tem(template_name)
		if template:
			# 字符串转字典
			template = eval(template.template_contents)
			print(template)
			t0 = time.perf_counter()
			to_email_type = (to_email.split("@"))[1]

			if to_email_type in self.real_mail:
				result = self.yag.send(to=to_email, contents=template["contents"], subject=template["subject"])
				maildb.my_email_counts(self.my_email)
			else:
				# 切换匿名邮件
				try:
					# 切换自己的匿名邮件服务器
					anon_mail = SMTP(user = None, password = None, host=None, port=None, proxy=self.proxy)
					result = anon_mail.send(to=to_email, contents=template["contents"], subject=template["subject"], fake_mail="admin@qq.com", fake_name="admin")
				except Exception:
					# 否则用当前邮箱进行发件人别名伪装
					result = self.yag.send(to=to_email, contents=template["contents"], subject=template["subject"], fake_mail="admin@qq.com", fake_name="admin")
					maildb.my_email_counts(self.my_email)
			t1 = time.perf_counter()
			time_long = t1-t0

			# 更新数据库
			maildb.send2db(self.my_email, to_email, template_name)
			maildb.to_email_counts(to_email)
			maildb.template_counts(template_name)
			self.send_result(result,time_long)
		else:
			print("[----] 邮件模板 %s 不存在" % template_name)


	def send_multiple(self,to_email_path, template_name):
		"""
		批量发送邮件
		"""
		error_email_path = os.path.splitext(os.path.split(to_email_path)[0])[0]+"/" + str(self.my_email) + ".txt"
		with open(to_email_path,"r",encoding="utf-8") as f:
			to_email_list = f.readlines()
		for to_email in to_email_list:
			to_email = to_email.strip()
			if len(to_email) != 0:
				pattern =r"^[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}$"
				if re.match(pattern,to_email):
					print("[++++] 正在处理邮箱：%s ..." % to_email)
					try:
						self.send_single(to_email=to_email, template_name=template_name)
					except Exception:
						print("[----] 处理邮箱 %s 失败！稍后请检查邮箱格式是否正确." % to_email)
						with open(error_email_path,"a+",encoding="utf-8") as f:
							f.write(to_email+"\n")
		if os.path.exists(error_email_path):
			print("[++++] 未成功发送的邮箱已保存至文件：error_%s.txt" % self.my_email)


