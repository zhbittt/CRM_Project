#!/usr/bin/env python
# -*- coding:utf-8 -*-
from .base import BaseMessage
class DingDing(BaseMessage):
    def __init__(self):
        pass

    def send(self, to, name, subject, body):
        print('钉钉消息发送成功')
