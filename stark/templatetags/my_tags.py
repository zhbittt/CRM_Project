from django import template

register = template.Library()

@register.inclusion_tag('stark/list.html')
def show_list(*args,**kwargs):
    data_list = kwargs["data_list"]
    header_list = kwargs["header_list"]
    return {"data_list":data_list,"header_list":header_list}


from django.db.models.query import QuerySet
from django.forms.models import ModelChoiceField
from django.shortcuts import reverse
from stark.service import v1
@register.inclusion_tag('stark/form.html')
def get_url(*args,**kwargs):
    form=kwargs["form"]
    config = kwargs["config"]
    new_form=[]
    for  bfield in form:
        # field是ModelForm读取对应的models.类，然后根据每一个数据库字段，生成Form的字段
        temp={"is_popup":False,"bfield":bfield}

        if isinstance(bfield.field,ModelChoiceField):
            related_app_model=bfield.field.queryset.model
            if related_app_model in v1.site._registry:
                # FK，One,M2M： 当前字段所在的类名和related_name
                model_name = config.model_class._meta.model_name #popup，表名
                related_name = config.model_class._meta.get_field(bfield.name).rel.related_name #popup , related_name
                # print(model_name,related_name)

                app_model_name = related_app_model._meta.app_label,related_app_model._meta.model_name

                base_url = reverse('stark:%s_%s_add'%app_model_name)
                popurl = "%s?_popbackid=%s&model_name=%s&related_name=%s"%(base_url,bfield.auto_id,model_name,related_name)
                temp["is_popup"] = True
                temp["popup_url"] = popurl
        new_form.append(temp)
    return {"form":new_form}