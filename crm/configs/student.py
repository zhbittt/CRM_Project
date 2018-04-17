import json

from django.conf.urls import url
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.shortcuts import render,HttpResponse,redirect
from crm.permissions.base import BasePermission
from crm import models
from stark.service import v1


class StudentConfig(BasePermission,v1.StarkConfig):

    def extra_url(self):
        app_model_name = (self.model_class._meta.app_label, self.model_class._meta.model_name,)
        patterns = [
            url(r'^(\d+)/sv/$', self.wrap(self.scores_view), name="%s_%s_sv" % app_model_name),
            url(r'^chart/$', self.wrap(self.scores_chart), name="%s_%s_chart" % app_model_name),
        ]
        return patterns

    def scores_view(self,request,sid):
        obj = models.Student.objects.filter(id=sid).first()
        if not obj:
            return HttpResponse('查无此人')
        class_list = obj.class_list.all()
        return render(request,'scores_view.html',{'class_list':class_list,'sid':sid})


    def scores_chart(self,request):
        ret = {'status':False,'data':None,'msg':None}
        try:
            cid = request.GET.get('cid')
            sid = request.GET.get('sid')
            record_list = models.StudyRecord.objects.filter(student_id=sid,course_record__class_obj_id=cid).order_by('course_record_id')
            data = [
                # ['day1', 24.25],
                # ['day2', 23.50],
                # ['day3', 21.51],
                # ['day4', 16.78],
                # ['day5', 16.06],
                # ['day6', 15.20]
            ]
            for row in record_list:
                day = "day%s" %row.course_record.day_num
                data.append([day,row.score])
            ret['data'] =data

            ret['status'] = True
        except Exception as e:
            ret['msg'] = "获取失败"

        return HttpResponse(json.dumps(ret))


    def display_scores(self,obj=None,is_header=False):
        if is_header:
            return "查看成绩"

        surls = reverse("stark:crm_student_sv",args=(obj.pk,))
        return mark_safe("<a href='%s'>点击查看</a>" %surls)

    list_display = ['username','emergency_contract',display_scores]