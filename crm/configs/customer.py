import datetime

from django.conf.urls import url
from django.db import transaction
from django.db.models import Q
from django.forms.models import ModelForm
from django.http import QueryDict
from django.shortcuts import redirect, HttpResponse, render
from django.utils.safestring import mark_safe
from django.http import FileResponse
from crm import models
from stark.service import v1
from Sale import AutoSale
from crm.permissions.customer import CustomerPersmission
import xlrd
# from xlrd.book import Book
# from xlrd.sheet import Sheet
# from xlrd.sheet import Cell

#方式1
# meta = type("Meta", (object,),
#             {"model": models.Customer, "exclude": ['consultant', 'status', 'recv_date', 'last_consult_date']})
# SingleModelForm = type("SingleModelForm", (ModelForm,), {"Meta": meta})
#方式2
class SingleModelForm(ModelForm):
    class Meta:
        model = models.Customer
        exclude = ['consultant','status','recv_date','last_consult_date']


class CustomerConfig(CustomerPersmission,v1.StarkConfig):

    def display_course(self,obj=None,is_header=None):
        if is_header:
            return "咨询课程"
        course_list=obj.course.all()

        # 跳转之前访问的页面
        list_condition = self.request.GET.urlencode()
        params = QueryDict(mutable=True)
        params[self._query_params_key] = list_condition
        params_condition = params.urlencode()

        html=[]
        for x in course_list:
            temp='<a href="/stark/crm/customer/%s/%s/dc/?%s" style="display:inline-block;  border:1px solid #1e4d7b ; padding: 3px 5px; margin:2px">%s X</a>'%(obj.pk,x.pk,params_condition,x.name)
            html.append(temp)
        return mark_safe("  ".join(html))

    def display_gender(self,obj=None,is_header=None):
        if is_header:
            return "性别"
        return obj.get_gender_display()

    def display_education(self,obj=None,is_header=None):
        if is_header:
            return "学历"
        return obj.get_education_display()

    def display_status(self,obj=None,is_header=None):
        if is_header:
            return "状态"
        return obj.get_status_display()

    def display_record(self,obj=None,is_header=None):
        if is_header:
            return "跟进记录"
        return mark_safe('<a href="/stark/crm/consultrecord/?customer=%s">查看跟进记录</a>'%obj.pk)

    def extra_url(self):
        nametuple = (self.model_class._meta.app_label, self.model_class._meta.model_name)
        url_patterns = [
            url(r'^(\d+)/(\d+)/dc/$', self.wrap(self.delete_course), name="%s_%s_dc"%nametuple),
            url(r'^public/$',self.wrap(self.public_view), name="%s_%s_public"%nametuple),
            url(r'^(\d+)/competition/$',self.wrap(self.competition_view), name="%s_%s_competition"%nametuple),
            url(r'^user/$',self.wrap(self.user_view), name="%s_%s_user"%nametuple),
            url(r'^single/$',self.wrap(self.single_view), name="%s_%s_single"%nametuple),
            url(r'^multi/$',self.wrap(self.multi_view), name="%s_%s_multi"%nametuple),
            url(r'^downfile/$',self.wrap(self.down_file), name="%s_%s_down"%nametuple),
        ]
        return url_patterns

    def delete_course(self,request,customer_id,course_id):
        customer_obj = models.Customer.objects.get(pk=customer_id)
        customer_obj.course.remove(course_id)

        oldurl = "%s?%s" % (self.get_list_url(), request.GET.get(self._query_params_key))
        return redirect(oldurl)

    def public_view(self,request):
        '''
        公共客户资源列表
        :param request:
        :return:
        '''

        #条件：未报名 并且  （15天未接单（当前时间-15 >  接客时间） or 3 天未跟进（当前时间 - 3 天 ＞　最后根据日期））　Ｑ对象
        current_user = 1

        # models.Customer.objects.filter(pk=5).update(
        #                 last_consult_date=datetime.datetime.strptime("2017-12-","%Y-%m-%d").date(),
        #                 recv_date=datetime.datetime.strptime("2017-12-12","%Y-%m-%d").date())
        # models.Customer.objects.filter(pk=8).update(
        #                 date=datetime.datetime.strptime("2017-12-11","%Y-%m-%d").date(),
        #                 last_consult_date=datetime.datetime.strptime("2017-12-12","%Y-%m-%d").date(),
        #                 recv_date=datetime.datetime.strptime("2017-12-11","%Y-%m-%d").date(),)
        # models.Customer.objects.filter(pk=9).update(
        #                 date=datetime.datetime.strptime("2017-12-2", "%Y-%m-%d").date(),
        #                 last_consult_date=datetime.datetime.strptime("2017-12-3","%Y-%m-%d").date(),
        #                 recv_date=datetime.datetime.strptime("2017-12-2","%Y-%m-%d").date())


        ctime = datetime.datetime.now().date()
        no_deal = ctime - datetime.timedelta(days=15) # 15天未接单
        no_follow  = ctime - datetime.timedelta(days=3) # 3天未跟进


        customer_list=models.Customer.objects.filter(Q(recv_date__lt=no_deal)|Q (last_consult_date__lt=no_follow),status=2)
        return render(request,'publish_view.html',{"customer_list":customer_list})

    def competition_view(self,request,customer_id):
        '''
        抢单操作
        :param request:
        :param customer_id: 客户id
        :return:
        '''
        #当前登录user
        current_user_id = 7

        #consultant 课程顾问 ,date  咨询日期,last_consult_date 最后跟进日期 ,recv_date 接客时间
        ctime = datetime.datetime.now().date()
        no_deal = ctime - datetime.timedelta(days=15) # 15天未接单
        no_follow  = ctime - datetime.timedelta(days=3) # 3天未跟进

        with transaction.atomic():
            records = models.Customer.objects.filter(Q(recv_date__lt=no_deal) | Q(last_consult_date__lt=no_follow)
                                                     , status=2,pk=customer_id).exclude(consultant_id=current_user_id).update(
                consultant_id=current_user_id, recv_date=ctime,
                last_consult_date=ctime)
            if not records:
                return HttpResponse("太慢了")
            models.CustomerDistribution.objects.create(user_id=current_user_id, customer_id=customer_id, ctime=ctime)
        return HttpResponse("抢单成功")

    def user_view(self,request):
        '''
        当前登录用户的所有客户
        :param request:
        :return:
        '''
        current_user = 8

        ctime = datetime.datetime.now().date()
        # ctime = datetime.datetime.strptime("2017-12-31","%Y-%m-%d").date()
        no_deal = ctime - datetime.timedelta(days=15) # 15天未成单
        no_follow  = ctime - datetime.timedelta(days=3) # 3天未跟进

        #查找当前登录用户CustomerDistribution，正在进行的所有客户
        customerdistribution_list=models.CustomerDistribution.objects.filter(status=1)

        # 15天未成单的客户
        no_deal_list = models.Customer.objects.filter(Q(recv_date__lt=no_deal),status=2)
        # 3天未跟进的客户
        no_follow_list = models.Customer.objects.filter(Q(last_consult_date__lt=no_follow),status=2).exclude(pk__in=no_deal_list)
        print("正在进行的所有客户=%s\n15天未成单=%s\n3天未跟进=%s\n"%(customerdistribution_list,no_deal_list,no_follow_list))
        for x in customerdistribution_list:
            if x.customer in no_deal_list:
                x.status = 4
            elif x.customer in no_follow_list:
                x.status = 3
            x.save()

        customer_list=models.CustomerDistribution.objects.filter(user_id=current_user)
        # customer_list=models.CustomerDistribution.objects.all()
        return render(request,'user_view.html',{"customer_list":customer_list})

    def single_view(self,request):
        """
        单条录入客户信息
        :param request:
        :return:
        """

        if request.method == "GET":
            form = SingleModelForm()
            return render(request,'single_view.html',{'form':form})
        else:

            form = SingleModelForm(request.POST)
            ctime = datetime.datetime.now().date()

            if form.is_valid():
                """客户表新增数据：
                    - 获取该分配的课程顾问id
                    - 当前时间
                 客户分配表中新增数据
                    - 获取新创建的客户ID
                    - 顾问ID
                """

                sale_id = AutoSale.get_sale_id()
                print(sale_id)
                # sale_id=7
                try:
                    with transaction.atomic():
                        # 方式一
                        # courses=form.cleaned_data.pop("course")
                        # new_customer = models.Customer.objects.create(**form.cleaned_data, consultant_id=sale_id,last_consult_date=ctime, recv_date=ctime,status=2)
                        # new_customer.course.add(*courses)
                        # new_customer.course.create()
                        # models.CustomerDistribution.objects.create(user_id=sale_id, customer=new_customer, ctime=ctime)

                        # 方式二 ---》不管用
                        # print(form.cleaned_data)
                        # obj=models.UserInfo.objects.get(pk=sale_id)
                        # form.cleaned_data["consultant"] = obj
                        # form.cleaned_data["last_consult_date"] = ctime
                        # form.cleaned_data["recv_date"] = ctime
                        # new_customer = form.save()
                        # models.CustomerDistribution.objects.create(user_id=sale_id, customer=new_customer, ctime=ctime)

                        # 方式三
                        form.instance.consultant_id = sale_id
                        form.instance.last_consult_date = ctime
                        form.instance.recv_date = ctime
                        new_customer = form.save()
                        models.CustomerDistribution.objects.create(user_id=sale_id, customer=new_customer, ctime=ctime)
                        print("单挑插入数据正确")

                except Exception:
                    AutoSale.rollback(sale_id)
                    print("单挑插入数据出错")
                oldurl = "%s?%s" % (self.get_list_url(), request.GET.get(self._query_params_key,""))
                return redirect(oldurl)
            else:
                return render(request, 'single_view.html', {'form': form})

    def multi_view(self,request):
        print(self.model_class._meta.app_label, self.model_class._meta.model_name)
        if request.method =="GET":
            return render(request,"multi_view.html")
        else:
            files_obj = request.FILES.get("exfile")
            # from django.core.files.uploadedfile import  InMemoryUploadedFile
            # print(files_obj,type(files_obj))
            # print(files_obj.field_name)
            # print(files_obj.size)
            # with open("excel.xlsx",'wb') as f:
            #     for chunk in files_obj:
            #         print(chunk,end="")
            #         f.write(chunk)
            # workbook = xlrd.open_workbook('excel.xlsx')
            # sheet_names = workbook.sheet_names()
            # sheet = workbook.sheet_by_name('工作表1')

            workbook = xlrd.open_workbook(file_contents=files_obj.read())
            sheet = workbook.sheet_by_index(0)

            maps={
                0:"name",
                1:"pwd"
            }
            excel_list=[]
            # 循环Excel文件的所有行
            for index in range(1,sheet.nrows):
                # 循环一行的所有列
                row = sheet.row(index)
                row_dict={}
                for i in range(len(maps)):
                    row_dict[maps[i]]=row[i].value
                excel_list.append(row_dict)
            print(excel_list)
            return HttpResponse("OK")


    # F:\Django_project\CRM_Project\stark\static\ExcelTemplate.xlsx
    # ExcelTemplate.xlsx

    def down_file(self,request):
        file = open("F:\Django_project\CRM_Project\stark\static\ExcelTemplate.xlsx","rb")
        response=FileResponse(file)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="Excel.xlsx"'
        return response

    list_display = ["qq","name",display_gender,display_education,display_course,display_status,display_record]
    list_order_by=['-status']
    edit_link = ["name"]
    # show_add_btn = False