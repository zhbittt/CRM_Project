#!/usr/bin/env python
# -*- coding:utf-8 -*-
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
from .base import BaseMessage


class Email(BaseMessage):
    def __init__(self):
        self.email = "1239225096@qq.com"
        self.user = "罗敏文"
        self.pwd = 'dtzwkzbabtqijbhh' #qq授权码

    def send(self,to,name,subject,body):
        msg = MIMEText(body,'plain','utf-8') #发送内容
        msg['From'] = formataddr([self.user,self.email]) #发件人
        msg['To'] = formataddr([name,to]) #收件人
        msg['subject'] = subject #主题

        server = smtplib.SMTP_SSL('smtp.qq.com',465) # SMTP服务
        # server = smtplib.SMTP('smtp.126.com',25) # SMTP服务
        server.login(self.email,self.pwd) #邮箱用户和密码
        server.sendmail(self.email,[to,],msg.as_string()) # 发送者和接收者
        server.quit()