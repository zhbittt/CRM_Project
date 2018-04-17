from stark.service import v1
from crm import models
from django.utils.safestring import mark_safe
from django.db import transaction
from crm.permissions.base import BasePermission
from crm.configs.customer import CustomerConfig
from crm.configs.student import StudentConfig
# class BasePermission(object):
#     def get_show_add_btn(self):
#         code_list = self.request.permission_code_list
#         if "add" in code_list:
#             return True
#
#     def get_edit_link(self):
#         code_list = self.request.permission_code_list
#         if "edit" in code_list:
#             return super(SchoolConfig,self).get_edit_link()
#         else:
#             return []
#
#     def get_list_display(self):
#         code_list = self.request.permission_code_list
#         data = []
#         if self.list_display:
#             data.extend(self.list_display)
#             if 'del' in code_list:
#                 data.append(v1.StarkConfig.delete)
#             data.insert(0, v1.StarkConfig.check_box)
#         return data


class DepartmentConfig(BasePermission,v1.StarkConfig):
    list_display = ["title","code"]
    edit_link = ["title"]
    # show_add_btn = True
    # show_query_field = True
    query_field = ["title__contains","code__contains"]
v1.site.registry(models.Department,DepartmentConfig)


class UserInfoConfig(BasePermission,v1.StarkConfig):
    def depart(self,obj=None,is_header=None):
        if is_header:
            return "所属部门"
        return obj.depart.title
    list_display = ["name","email",depart]
    edit_link = ["name"]
    # show_add_btn = True
    # show_query_field = True
    query_field = ["name__contains","email__contains"]
    # show_comb_filter = True
    comb_filter = [
        v1.FilterOption("depart",text_func_name=lambda x : str(x),val_func_name = lambda x : x.code)
    ]
v1.site.registry(models.UserInfo,UserInfoConfig)


class CourseConfig(v1.StarkConfig):
    list_display = ["name"]
    edit_link = ["name"]
    # show_add_btn = True
v1.site.registry(models.Course,CourseConfig)


class SchoolConfig(BasePermission,v1.StarkConfig):
    list_display = ["title"]
    edit_link = ["title"]
    # show_add_btn = True
v1.site.registry(models.School,SchoolConfig)


class ClassListConfig(BasePermission,v1.StarkConfig):
    def course_semester(self,obj=None,is_header=None):
        if is_header:
            return "班级"
        return "%s(%s期)"%(obj.course.name,obj.semester)

    def start_date(self,obj=None,is_header=None):
        if is_header:
            return "开班日期"
        return obj.start_date.strftime("%Y-%m-%d")

    def cls_num(self,obj=None,is_header=None):
        if is_header:
            return "班级人数"
        a = models.Student.objects.filter(class_list=obj.pk).count()

        return a
    list_display = ["school","course",course_semester,cls_num,start_date]
    edit_link = ["school"]
    # show_add_btn = True
v1.site.registry(models.ClassList,ClassListConfig)


class ConsultRecordConfig(v1.StarkConfig):
    def display_customer(self,obj=None,is_header=None):
        if is_header:
            return "所咨询客户"
        return obj.customer.name

    def display_consultant(self,obj=None,is_header=None):
        if is_header:
            return "跟踪人"
        return obj.consultant.name

    def display_date(self,obj=None,is_header=None):
        if is_header:
            return "跟进日期"
        return obj.date.strftime("%Y-%m-%d")

    def display_note(self, obj=None, is_header=None):
        if is_header:
            return "跟进内容"
        return obj.note

    list_display = [display_customer,display_consultant,display_date,display_note]
    # show_add_btn = True

    edit_link = [display_customer]
    comb_filter = [
        v1.FilterOption("customer")
    ]

    # def changelist_view(self,request,*args,**kwargs):
    #     customer = request.GET.get("customer")
    #
    #     current_login_id = 7
    #     ct=models.Customer.objects.filter(consultant=current_login_id,id=customer).count()
    #     if not ct:
    #         return HttpResponse("别抢客户")
    #     return super(ConsultRecordConfig,self).changelist_view(request,*args,**kwargs)
v1.site.registry(models.ConsultRecord,ConsultRecordConfig)


# class StudentConfig(v1.StarkConfig):
#
#     def class_list(self,obj=None,is_header=None):
#         if is_header:
#             return "所在班级"
#         cls_obj=models.ClassList.objects.filter(student__id=obj.pk).first()
#         return "%s(%s期)"%(cls_obj.course.name,cls_obj.semester)
#
#     list_display = ["username",class_list]
#     edit_link = ["username"]
#     show_add_btn = True



class CourseRecordConfig(v1.StarkConfig):
    def display_class_obj(self,obj=None,is_header=None):
        if is_header:
            return "班级"
        return "%s(%s期)"%(obj.class_obj.course,obj.class_obj.semester)

    def kaoqin(self,obj=None,is_header=None):
        if is_header:
            return "考勤"
        return mark_safe('<a href="/stark/crm/studyrecord/?course_record=%s">考勤管理</a>'%obj.pk)


    list_display = [display_class_obj,"day_num",kaoqin]
    # show_add_btn = True
    # show_actions = True

    #定制actions
    def multi_init(self,requset):
        '''
        初始化学生上课记录
        :param requset:
        :return:
        '''
        pk_list = requset.POST.getlist('pk')
        print(pk_list)
        with transaction.atomic():
            for pk in pk_list:
                course_obj=models.CourseRecord.objects.filter(pk=pk).first()
                studyrecord_obj=models.StudyRecord.objects.filter(course_record=course_obj)
                if not studyrecord_obj:
                    student_list = models.Student.objects.filter(class_list=course_obj.class_obj.pk)

                    bulk_list=[]
                    for stu in student_list:
                        bulk_list.append(models.StudyRecord(course_record=course_obj,record="checked",student_id=stu.pk))
                    models.StudyRecord.objects.bulk_create(bulk_list)
                else:
                    print("%s已经初始化了"%course_obj)
    multi_init.short_desc = "学生初始化"


    list_acions = [multi_init]
v1.site.registry(models.CourseRecord,CourseRecordConfig)


class StudyRecordConfig(v1.StarkConfig):
    def display_course_record(self,obj=None,is_header=None):
        if is_header:
            return "第几天课程"
        return "%s(%s期) day%s"%(obj.course_record.class_obj.course.name,obj.course_record.class_obj.semester,obj.course_record.day_num)

    def display_student(self,obj=None,is_header=None):
        if is_header:
            return "学员"
        return obj.student.customer.name
    def display_record(self,obj=None,is_header=None):
        if is_header:
            return "出勤"
        return obj.get_record_display()
    list_display = [display_course_record,display_student,display_record]

    # show_add_btn = False
    # show_comb_filter = True
    comb_filter = [
        v1.FilterOption("course_record",),
    ]

    def multi_checked(self,request):
        pk_list=request.POST.getlist("pk")
        #['1', '2', '3']
        for pk in pk_list:
            models.StudyRecord.objects.filter(pk=pk).update(record="checked")
    multi_checked.short_desc ="已签到"

    def multi_vacate(self,request):
        pk_list = request.POST.getlist("pk")
        for pk in pk_list:
            models.StudyRecord.objects.filter(pk=pk).update(record="vacate")
    multi_vacate.short_desc ="请假"

    def multi_late(self,request):
        pk_list = request.POST.getlist("pk")
        for pk in pk_list:
            models.StudyRecord.objects.filter(pk=pk).update(record="late")
    multi_late.short_desc ="迟到"

    def multi_noshow(self,request):
        pk_list = request.POST.getlist("pk")
        for pk in pk_list:
            models.StudyRecord.objects.filter(pk=pk).update(record="noshow")
    multi_noshow.short_desc ="缺勤"

    def multi_leave_early(self,request):
        pk_list = request.POST.getlist("pk")
        for pk in pk_list:
            models.StudyRecord.objects.filter(pk=pk).update(record="leave_early")
    multi_leave_early.short_desc ="早退"

    # show_actions = True
    list_acions = [multi_checked,multi_vacate,multi_late,multi_noshow,multi_leave_early]
v1.site.registry(models.StudyRecord,StudyRecordConfig)


class SaleRankConfig(v1.StarkConfig):
    def display_user(self,obj=None,is_header=None):
        if is_header:
            return "客户顾问"
        return obj.user.name

    list_display = [display_user,"num","weight"]

    # show_add_btn = True

    edit_link = [display_user]
v1.site.registry(models.SaleRank,SaleRankConfig)


class CustomerDistributionConfig(v1.StarkConfig):
    def display_user(self,obj=None,is_header=None):
        if is_header:
            return "客户顾问"
        return obj.user.name

    def display_customer(self,obj=None,is_header=None):
        if is_header:
            return "客户"
        return obj.customer.name

    def display_status(self,obj=None,is_header=None):
        if is_header:
            return "状态"
        return obj.get_status_display()

    list_display = [display_user,display_customer,display_status,"memo"]
    # show_add_btn = False
    edit_link = [display_user]
v1.site.registry(models.CustomerDistribution,CustomerDistributionConfig)



v1.site.registry(models.PaymentRecord)
v1.site.registry(models.Student,StudentConfig)
v1.site.registry(models.Customer,CustomerConfig)