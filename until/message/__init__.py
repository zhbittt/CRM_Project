import importlib
from django.conf import settings

def send_message(to,name,subject,body):
    '''
    短信，微信，邮箱
    :param to: 接收者
    :param name: 接收者姓名
    :param subject: 主题
    :param body: 内容
    :return:
    '''
    print(settings.MESSAGE_CLASSES)
    for cls_path in settings.MESSAGE_CLASSES:
        print(cls_path)
        # cls_path 例如：'unitl.message.email.Email',
        model_path,class_name =cls_path.rsplit(".",maxsplit=1)
        m=importlib.import_module(model_path)
        obj=getattr(m,class_name)()
        obj.send(to,name,subject,body)
