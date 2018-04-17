#!/usr/bin/env python
# -*- coding:utf-8 -*-
# 方式一
# from abc import ABCMeta
# from abc import abstractmethod
#
# class BaseMessage(metaclass=ABCMeta):
#
#     @abstractmethod
#     def send(self,subject,body,to,name):
#         pass

# 方式二
class BaseMessage(object):
    def send(self, to, name, subject, body):
        raise NotImplementedError('未实现send方法')
