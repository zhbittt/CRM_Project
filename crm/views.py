from django.db.models import Count
from django.shortcuts import render,HttpResponse,redirect
from until import message
from crm import models
from rbac import models as rbac_model
from rbac.service.init_permission import init_permission
import json
import datetime
from io import BytesIO
import random

from PIL import Image, ImageDraw, ImageFont

def eee(requset):
    message.send_message('522338473@qq.com', 'zhangjianping', '主题：测试发送邮件', '邮件内容为：sssssssssssssssssssssssssssssss')
    return HttpResponse("OK")

def month_single_count(request):
    import datetime
    # datetime.datetime.strftime()
    data_list = models.CustomerDistribution.objects.filter(ctime__year=2017,status=2).extra(
        select={'mt':'strftime("%%Y-%%m",ctime)'}).values_list("mt").annotate(ct=Count('id'))
    data =[0 for x in range(12)]
    for d,c in data_list:
        num=int(d.rsplit("-")[1])
        data[num-1]=c
    return render(request, 'month_single_count.html',{"data":data})

def month_single_rate(request):
    v1 = models.CustomerDistribution.objects.filter(ctime__year=2017, status=2).extra(
        select={'mt': 'strftime("%%Y-%%m",ctime)'}).values_list('mt').annotate(ct=Count('id'))

    v2 = models.CustomerDistribution.objects.filter(ctime__year=2017).extra(
        select={'mt': 'strftime("%%Y-%%m",ctime)'}).values_list('mt').annotate(ct=Count('id'))

    data =[0 for x in range(12)]
    for bv1,bv2 in zip(v1,v2):
        num=int(bv2[0].rsplit("-")[1])
        data[num - 1] = 0 if bv2[1]==0 else bv1[1]/bv2[1]
    return render(request,'month_single_rate.html',{"data":data})

def month_user_count(request):
    start_date = datetime.datetime.strptime('2017-1','%Y-%m').date()
    end_date  = datetime.datetime.now().date()
    print(start_date)
    print(end_date)
    all_list = models.CustomerDistribution.objects.filter(ctime__gte=start_date,
        ctime__lte=end_date, status=2).extra(
        select={'mt': 'strftime("%%Y-%%m",ctime)'}).values_list(
         'mt','user_id')
    print(all_list)

    data =[0 for x in range(12)]
    for d,c in all_list:
        num = int(d.rsplit("-")[1])
        data[num - 1] = c
    return render(request,'month_user_count.html',{"data":data})

def login(request):
    msg = ""
    if request.method =='GET':
        return render(request, 'login.html',{"msg":msg})
    else:
        username = request.POST.get("username")
        password = request.POST.get("password")
        validCode = request.POST.get("validCode")

        if validCode.upper() == request.session.get("keepValidCode").upper():
            user =rbac_model.User.objects.filter(username=username, password=password).first()
            if user:
                # 表示已登录
                request.session['user_info'] = {'user_id': user.id, 'uid': user.userinfo.id, 'name': user.userinfo.name}
                # 权限写入session
                init_permission(user, request)
                # 跳转
                return redirect('/index/')
            else:
                msg = "账号或密码错误"
        else:
            msg = "验证码错误"
        return render(request, 'login.html',{"msg":msg})


# def login(request):
#     if request.method == "GET":
#         return render(request,'login.html')
#     else:
#         user = request.POST.get('username')
#         pwd = request.POST.get('password')
#         user = rbac_model.User.objects.filter(username=user,password=pwd).first()
#
#         if user:
#             # 表示已登录
#             request.session['user_info'] = {'user_id':user.id,'uid':user.userinfo.id,'name':user.userinfo.name}
#             # 权限写入session
#             init_permission(user,request)
#             # 跳转
#             return redirect('/index/')
#
#         return render(request, 'login.html')


def get_validCode_img(request):

    img = Image.new(mode="RGB", size=(120, 40), color=(random.randint(0,255),random.randint(0,255),random.randint(0,255)))

    draw=ImageDraw.Draw(img,"RGB")

    font=ImageFont.truetype("static/font/kumo.ttf",25)

    valid_list=[]
    for i in range(5):

        random_num=str(random.randint(0,9))
        random_lower_zimu=chr(random.randint(65,90))
        random_upper_zimu=chr(random.randint(97,122))

        random_char=random.choice([random_num,random_lower_zimu,random_upper_zimu])
        draw.text([5+i*24,10],random_char,(random.randint(0,255),random.randint(0,255),random.randint(0,255)),font=font)
        valid_list.append(random_char)


    f=BytesIO()
    img.save(f,"png")
    data=f.getvalue()

    valid_str="".join(valid_list)
    print(valid_str)

    request.session["keepValidCode"]=valid_str

    return HttpResponse(data)


def index(request):
    return render(request,'index.html')