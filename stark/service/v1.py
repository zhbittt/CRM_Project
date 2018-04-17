from django.conf.urls import url
from django.shortcuts import render,HttpResponse,redirect
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.forms import ModelForm
from django.http import QueryDict
from django.db.models import Q
from until.pager1 import Pagination
from django.db.models import ForeignKey
from django.db.models import ManyToManyField

import copy
import json

class FilterOption(object):
    '''
    根据字段返回表里数据
    '''
    def __init__(self,field_name,multi=False,condition=None,is_choice=False,text_func_name=None,val_func_name=None):
        '''
        :param field_name: 字段
        :param multi:  是否多选
        :param condition: 显示数据的筛选条件
        :param is_choice: 是否是choice
        '''
        self.field_name = field_name
        self.multi = multi
        self.condition = condition
        self.is_choice =is_choice
        self.text_func_name = text_func_name #不是根据pk来搜索，例如 code=1001
        self.val_func_name = val_func_name  #同上 ，用法：text_func_name=lambda x: str(x), val_func_name=lambda x: x.code
    def get_queryset(self,_field):
        if self.condition:
            return _field.rel.to.objects.filter(**self.condition)
        return _field.rel.to.objects.all()

    def get_choices(self,_field):
        '''
        获取字段的choices
        '''
        return _field.choices


class FilterRow(object):
    '''
    生成组合搜索的链接
    '''
    def __init__(self,option,data,request):
        self.option = option
        self.data = data
        self.request = request
    def __iter__(self):
        #data =
        # [(0,男)，(1,女)]
        # [ obj , obj obj ]

        path_info=self.request.path_info
        params = copy.deepcopy(self.request.GET)
        params.mutable = True
        current_id = params.get(self.option.field_name)
        current_id_list = params.getlist(self.option.field_name)
        if "page" in params:
            params.pop("page")
        if self.option.field_name in params:
            origin_list = params.pop(self.option.field_name)
            yield mark_safe('<a href="{0}?{1}">全部</a>'.format(path_info,params.urlencode()))
            params.setlist(self.option.field_name, origin_list)
        else:
            yield mark_safe('<a href="{0}?{1}" class="active">全部</a>'.format(path_info,params.urlencode()))
        for val in self.data:
            if self.option.is_choice:
                pk,text = str(val[0]),val[1]
            else:
                text = str(self.option.text_func_name(val)) if self.option.text_func_name else str(val)
                pk = str(self.option.val_func_name(val)) if self.option.val_func_name else str(val.pk)


            if not self.option.multi:
                params[self.option.field_name] = pk
                if pk == current_id:
                    yield mark_safe( '<a href="{0}?{1}" class="active" >{2}</a>'.format(path_info, params.urlencode(), text))
                else:
                    yield mark_safe('<a href="{0}?{1}" >{2}</a>'.format(path_info, params.urlencode(), text))
            else:
                _params = copy.deepcopy(params)
                id_list = _params.getlist(self.option.field_name)
                if pk in current_id_list:
                    id_list.remove(pk)
                    _params.setlist(self.option.field_name,id_list)
                    yield mark_safe('<a href="{0}?{1}" class="active" >{2}</a>'.format(path_info, _params.urlencode(), text))
                else:
                    id_list.append(pk)
                    _params.setlist(self.option.field_name, id_list)
                    yield mark_safe('<a href="{0}?{1}" >{2}</a>'.format(path_info, _params.urlencode(), text))


class ChangeList(object):
    def __init__(self,config,obj_list):
        self.config = config
        self.request = config.request
        self.obj_list = obj_list
        self.obj_list_count=obj_list.count()
        self.get_list_display = config.get_list_display()
        self.model_class = config.model_class
        self.comb_filter = config.get_comb_filter()
        self.edit_link = config.get_edit_link()
        #分页对象

        self.pager_obj = Pagination(config,self.obj_list_count, config.request.path_info)

    def add_url(self):
        '''
        添加按钮的url
        '''
        # 保存页面跳转的信息
        params = QueryDict(mutable=True)
        params[self.config._query_params_key] = self.config.request.GET.urlencode()
        list_condition=params.urlencode()
        if list_condition:
            ret = "%s?%s"%(self.config.get_add_url(),list_condition)
        else:
            ret = self.config.get_add_url()
        return  ret

    def header_data(self):
        '''
        列表标题
        '''
        for header_name in self.get_list_display:
            if isinstance(header_name, str):
                field_verbose_name = self.model_class._meta.get_field(header_name).verbose_name
            else:
                field_verbose_name = header_name(self.config, is_header=True)
            yield field_verbose_name

    def data_list(self):
        '''
        列表内容
        '''
        for obj in self.obj_list[self.pager_obj.start:self.pager_obj.end]:

            def inner(obj):
                for field_name in self.get_list_display:
                    if isinstance(field_name, str):
                        val = getattr(obj, field_name)
                    else:
                        val = field_name(self.config, obj)

                    if field_name in self.edit_link:
                        val = self.edit_link_tag(obj.pk,val)
                    yield val
            yield inner(obj)

    def edit_link_tag(self,pk,val):

        list_condition = self.request.GET.urlencode()
        params=QueryDict(mutable=True)
        params[self.config._query_params_key]=list_condition
        params_condition = params.urlencode()
        return mark_safe('<a href="%s?%s">%s</a>'%(self.config.get_change_url(pk),params_condition,val))

    def modify_actions(self):
        '''
        返回action，例：批量删除，初始化功能
        '''
        result=[]
        for x in self.config.get_list_acions():
            result.append({"name":x.__name__,"text":x.short_desc})

        return result



    def gen_comb_filter(self):
        '''
        组合查询显示
        '''
        for option in self.comb_filter:
            _field=self.model_class._meta.get_field(option.field_name)
            if isinstance(_field,ForeignKey):
                row = FilterRow(option,option.get_queryset(_field),self.request)
            elif isinstance(_field,ManyToManyField):
                row = FilterRow(option,option.get_queryset(_field),self.request)
            else:
                row = FilterRow(option,option.get_choices(_field),self.request)
            yield row


class StarkConfig(object):

    def __init__(self,model_class,site):
        self.model_class = model_class
        self.site= site
        self.request = None
        self._query_params_key='_list_filter'

    # ##################跳转之前？的数据##################
    # def get_params_condition(self,request):
    #     list_condition = request.GET.urlencode()
    #     params = QueryDict(mutable=True)
    #     params[self._query_params_key] = list_condition
    #     params_condition = params.urlencode()

    ##################点击字段可编辑##################
    show_edit_link = False
    edit_link = []
    def get_show_edit_link(self):
        return self.show_edit_link

    def get_edit_link(self):
        result = []
        if self.edit_link:
            result.extend(self.edit_link)
        return result


    ##################列表显示的字段##################
    list_display = []

    def get_list_display(self):
        '''
        #获取表里边或者自定义要显示的字段
        #
        #如果使用self.list_display去append--edit，delete，check_box。那么下次刷新页面会继续添加edit，delete，check_box
        #第一次[check_box，"id","name",edit,delete]  第二次[check_box，"id","name",edit,delete,check_box，"id","name",edit,delete]
        '''
        data = []
        if self.list_display:
            data.extend(self.list_display)
        else:
            # 默认显示表里边所有的字段
            data = [x.name for x in self.model_class._meta.fields]
        # data.append(StarkConfig.edit)
        data.append(StarkConfig.delete)
        data.insert(0, StarkConfig.check_box)
        return data

    ###############添加功能的按钮######
    show_add_btn = True

    def get_show_add_btn(self):
        return self.show_add_btn

    ###################关键字搜索#######
    query_field = []
    show_query_field = False

    def get_show_query_field(self):
        return self.show_query_field

    def get_query_field(self):
        result=[]
        if self.query_field:
            result.extend(self.query_field)
        return result

    def get_search_condition(self):
        query_key = self.request.GET.get("q", "")
        condition = Q()
        condition.connector = "OR"
        for field in self.get_query_field():
            condition.children.append((field, query_key))
        return condition

    #################action显示######

    #自定义actions
    def multi_del(self,requset):
        pk_list = requset.POST.getlist('pk')
        self.model_class.objects.filter(pk__in=pk_list).delete()
    multi_del.short_desc='批量删除'

    def multi_init(self, requset):
        pk_list = requset.POST.getlist('pk')
    multi_init.short_desc='初始化'

    def multi_default(self, requset):
        pass
    multi_default.short_desc='请选择action'

    list_acions = []


    show_actions = False
    def get_show_actions(self):
        return self.show_actions

    def get_list_acions(self):
        result=[]
        result.append(self.multi_default)
        if self.list_acions:
            result.extend(self.list_acions)

        return result

    #################组合搜索######
    show_comb_filter = False

    def get_show_comb_filter(self):
        return self.show_comb_filter

    comb_filter = []
    def get_comb_filter(self):
        result = []
        if self.comb_filter:
            result.extend(self.comb_filter)
        return result

    #################添加排序条件######
    list_order_by=[]
    def get_order_by(self):
        result = []
        result.extend(self.list_order_by)
        return result

    ###################列表显示页面，默认添加的字段#######
    def check_box(self,obj=None,is_header=False):
        '''
        列表显示添加check_box字段
        '''
        if is_header:
            return "选择"
        return mark_safe('<input type="checkbox" name="pk" value="%s">'%obj.id)

    def edit(self,obj=None,is_header=False):
        '''
        列表显示添加编辑字段
        '''
        if is_header:
            return "编辑"

        list_condition = self.request.GET.urlencode()
        params=QueryDict(mutable=True)
        params[self._query_params_key]=list_condition
        params_condition = params.urlencode()

        if list_condition:
            tag_a=mark_safe('<a href="%s?%s">编辑</a>' % (self.get_change_url(obj.id), params_condition))
        else:
            tag_a = mark_safe('<a href="%s">编辑</a>' % (self.get_change_url(obj.id)))
        return tag_a

    def delete(self,obj=None,is_header=False):
        '''
        列表显示添加删除字段
        '''
        list_condition = self.request.GET.urlencode()
        params = QueryDict(mutable=True)
        params[self._query_params_key] = list_condition
        params_condition = params.urlencode()

        if is_header:
            return "删除"
        if list_condition:
            tag_a=mark_safe('<a href="%s?%s">删除</a>' % (self.get_delete_url(obj.id), params_condition))
        else:
            tag_a = mark_safe('<a href="%s">删除</a>'%(self.get_delete_url(obj.id)))
        return tag_a



    ##################反向生产url##################
    def get_change_url(self,nid):
        '''
        获取修改的url
        '''
        name = "stark:%s_%s_change"%(self.model_class._meta.app_label,self.model_class._meta.model_name)
        get_url = reverse(name,args=(nid,))
        return get_url

    def get_list_url(self):
        '''
        获取查询的url
        '''
        name = "stark:%s_%s"%(self.model_class._meta.app_label,self.model_class._meta.model_name)
        get_url = reverse(name)
        return get_url

    def get_add_url(self):
        '''
        获取添加的url
        '''
        name = "stark:%s_%s_add" % (self.model_class._meta.app_label, self.model_class._meta.model_name)
        get_url = reverse(name)
        return get_url

    def get_delete_url(self,nid):
        '''
        获取删除的url
        '''
        name = "stark:%s_%s_delete"%(self.model_class._meta.app_label,self.model_class._meta.model_name)
        get_url = reverse(name,args=(nid,))
        return get_url

    ################## url对应的视图函数##################

    #单例模式
    model_form_class = None
    def get_model_form_class(self):
        if self.model_form_class:
            return self.model_form_class

        meta = type('Meta',(object,),{'model':self.model_class,"fields":"__all__"})
        TestModelForm = type('TestModelForm',(ModelForm,),{'Meta':meta})

        return TestModelForm


    def changelist_view(self,request):
        '''
        列表显示视图函数
        '''
        if request.method=="POST":
            func_name_str=request.POST.get("list_action")
            func = getattr(self,func_name_str)
            ret = func(request)
            if ret:
                return ret

        comb_condition = {}
        option_list = self.get_comb_filter()
        for key in request.GET.keys():
            value_list = request.GET.getlist(key)
            flag = False
            for option in option_list:
                if option.field_name == key:
                    flag = True
                    break
            if flag:
                comb_condition["%s__in" %key] = value_list

        obj_list=self.model_class.objects.filter(self.get_search_condition()).filter(**comb_condition).order_by(*self.get_order_by()).distinct()
        # obj_list=self.model_class.objects.filter(gender__in=['2'],depart__in=['1'],id__contains='',name__contains='').distinct()

        changelist=ChangeList(self,obj_list)
        return render(request,'stark/list_view.html',{"changelist":changelist})


    def add_view(self,request):
        '''
        添加视图函数
        '''
        model_form_class=self.get_model_form_class()

        if request.method =="GET":
            form = model_form_class()
            return render(request,'stark/add_view.html',{"form":form,"config":self})
        else:
            form = model_form_class(request.POST)
            _popbackid = request.GET.get("_popbackid")
            result = {"status":False,"id": None, "text": None, "popbackid": _popbackid}

            if form.is_valid():
                print(form.cleaned_data)
                new_obj=form.save()
                if _popbackid:
                    model_name = request.GET.get("model_name")
                    related_name = request.GET.get("related_name")

                    from django.db.models.fields.reverse_related import ManyToOneRel
                    for related_object in new_obj._meta.related_objects:
                        _model_nmae = related_object.field.model._meta.model_name
                        _related_name = related_object.related_name
                        _limit_choices_to = related_object.limit_choices_to
                        if (type(related_object) == ManyToOneRel):
                            _field_name = related_object.field_name
                        else:
                            _field_name = 'pk'
                        print(model_name == _model_nmae,related_name == str(_related_name))
                        if model_name == _model_nmae and related_name == str(_related_name):
                            is_exists = self.model_class.objects.filter(**_limit_choices_to,pk=new_obj.pk).exists()
                            print("is_exists",is_exists)
                            if is_exists:
                                result["status"]= True
                                result["text"]= str(new_obj)
                                result["id"]= getattr(new_obj,_field_name)
                                print("1",result)
                                return render(request,'stark/popup_response.html',
                                              {"json_result":json.dumps(result,ensure_ascii=False)})
                    else:
                        print("2",result)
                        return render(request, 'stark/popup_response.html',
                                      {"json_result": json.dumps(result, ensure_ascii=False)})

                oldurl = "%s?%s" % (self.get_list_url(), request.GET.get(self._query_params_key))
                return redirect(oldurl)
            return render(request,'stark/add_view.html',{"form":form,"config":self})

    def change_view(self,request,nid):
        '''
        修改视图函数
        '''
        obj = self.model_class.objects.filter(pk=nid).first()
        model_form_class = self.get_model_form_class()
        if request.method =='GET':
            form = model_form_class(instance=obj)
            return render(request, 'stark/change_view.html', {"form":form,"config":self})
        else:
            form = model_form_class(instance=obj,data=request.POST)
            if form.is_valid():
                form.save()
                oldurl="%s?%s"%(self.get_list_url(),request.GET.get(self._query_params_key))
                return redirect(oldurl)
            return render(request, 'stark/change_view.html', {"form": form,"config":self})

    def delete_view(self,request,nid):
        '''
        删除视图函数
        '''

        if request.method=="GET":
            return render(request,'stark/delete_view.html')
        else:
            self.model_class.objects.filter(pk=nid).delete()
            oldurl = "%s?%s" % (self.get_list_url(), request.GET.get(self._query_params_key,""))
        return redirect(oldurl)





    ##################生成url##################
    def wrap(self,view_func):
        def inner(requset,*args,**kwargs):
            self.request = requset
            return view_func(requset,*args,**kwargs)
        return inner

    def get_urls(self):
        '''
        给正则表达式定义个别名，name = 应用名_表名_对应操作 例：name = app01_Author_add
        '''
        nametuple = (self.model_class._meta.app_label, self.model_class._meta.model_name)
        url_patterns = [
            url(r'^$', self.wrap(self.changelist_view), name="%s_%s"%nametuple),
            url(r'^add/$', self.wrap(self.add_view), name="%s_%s_add"%nametuple),
            url(r'^(\d+)/change/$', self.wrap(self.change_view), name="%s_%s_change"%nametuple),
            url(r'^(\d+)/delete/$', self.wrap(self.delete_view), name="%s_%s_delete"%nametuple),
        ]
        url_patterns.extend(self.extra_url())
        return url_patterns

    ###################自定义添加额外的url##################
    def extra_url(self):
        return []

    @property
    def urls(self):
        return self.get_urls()


class StarkSite(object):

    def __init__(self):
        self._registry = {}

    def registry(self,model_class,stark_config_class=None):
        if not stark_config_class:
            stark_config_class = StarkConfig
        self._registry[model_class]=stark_config_class(model_class,self)#self是site对象

    def get_urls(self):

        url_patterns = []
        for model_class,start_config_obj in self._registry.items():
            # model_class._meta.app_label   获取应用名
            # model_class._meta.model_name   获取表名

            url_patterns +=[
                url(r'^%s/%s/'% (model_class._meta.app_label, model_class._meta.model_name),
                    (start_config_obj.urls,None,None))
            ]

        return url_patterns

    @property
    def urls(self):
        return self.get_urls(),None,'stark'

site = StarkSite()


