#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
参考：
    https://www.jianshu.com/p/491ee88f27a6
    https://www.kancloud.cn/smilesb101/python3_x/298894
echo "邮件正文" | mailx -s 邮件主题 sdw3dw@protonmail.com -r admin@xx.xx
"""

from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import smtplib

class MailNoReply(object):
    def __FormatAddress(self, text):
        name, addr = parseaddr(text)
        return formataddr((Header(name, 'utf8').encode(), addr))

    def SendOneMail(self, sender, receiver, subject, content):
        '''
        利用本地sendmail服务发一封信
        :param sender: [string] 发信人地址 xx@yy.zz 格式，可杜撰
        :param receiver: [string] 收信人地址 xx@yy.zz 格式，需真实存在
        :param subject: [string] 邮件主题
        :param content: [string] 邮件内容
        :return: True/False 成功/失败
        '''
        try:
            message = MIMEText(content, 'plain', 'utf8')
            message['From'] = self.__FormatAddress('收件人名称（随便写） <%s>' % sender)
            message['To'] = self.__FormatAddress('收件人名称（随便写） <%s>' % receiver)
            message['Subject'] = Header(subject, 'utf8').encode()

            smtpObj = smtplib.SMTP(host='localhost')
            smtpObj.sendmail(sender, [receiver], message.as_string())
            return True
        except smtplib.SMTPException as msg:
            print(msg)

if __name__ == "__main__":
    from datetime import datetime
    import random
    random_password = ''.join(str(i) for i in random.sample(range(0, 9), 6))
    email = "test@qq.com"
    foo = MailNoReply()
    foo.SendOneMail('666@qq.com', email, '密码重置','亲爱的客户,您于%s发起密码重置，新密码为%s，如非本人操作请速联系管理员!' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), random_password))


