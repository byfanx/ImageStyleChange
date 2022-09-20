from django.shortcuts import render,HttpResponse
import json
import time
from userApp.models import *
from imgsApp.views import IMGS_URL
from hashlib import md5

from ImageStyleChange import settings
# Create your views here.
def hello(req):
    # data = {
    #     'flag': 1,
    #     'msg': '用户名已存在!',
    # }
    # data['aa'] = 'aaa'
    # print(data)
    return render(req, 'hello.html')

    # image = "1.jpg"
    # da = {"str":"Hello,World!","imgUrl":image}
    # cid = req.GET.get('username')
    # print(cid)
    # flag = User.objects.filter(username=cid).exists()
    # print(flag)
    # userApp = User.objects.get(username=cid)
    # if userApp:
    #     print("id="+str(userApp.id)+"\tusername="+str(userApp.username)+"\tpassword="+str(userApp.password)+"\tavatarUrl="+str(userApp.avatarUrl))
    # print(userApp)
    # return render(req, "hello.html", da)

def index(req):
    return render(req,'login.html')

def register(req):
    if req.method == "POST":
        data = {
            'flag': 0
        }
        reqData = req.POST
        username = reqData.get('username')
        email = reqData.get('email')
        password = reqData.get('password')
        repassword = reqData.get('repassword')
        user = User(username=username, email=email, password=password)
        data['user'] = user;
        if username=="":
            data['msg'] = '用户名不能为空'
            return render(req, 'login.html', data)
        if email=="":
            data['msg'] = '邮箱不能为空'
            return render(req, 'login.html', data)
        if password=="":
            data['msg'] = '密码不能为空'
            return render(req, 'login.html', data)
        if repassword=="":
            data['msg'] = '确认密码不能为空'
            return render(req, 'login.html', data)

        print(username,email,password,repassword)

        userlist = User.objects.filter(username=username)
        if userlist.exists():
            '''如果用户名存在，返回信息，重新注册'''
            data['msg'] = '用户名已存在'
            # return render(req,'login.html',data)
        elif password != repassword:
            '''如果两次密码不一致不给注册'''
            data['msg'] = '两次密码不一致'
            # return render(req, 'login.html', data)
        else:
            '''如果用户名不存在且两次密码一致，注册用户'''
            # 使用md5算法对密码进行加密
            passwd = md5(password.encode('utf-8')).hexdigest();
            user = User.objects.create(username=username,email=email,password=passwd)
            data['user'] = user
            data['msg'] = '注册成功,开始登录吧'
            # return render(req,'login.html',data)


        # print("username="+str(username)+"\tpassword="+str(password)+"\tavatarUrl="+str(avatarUrl))

        return render(req,'login.html',data)

def login(req):
    if req.method == 'POST':
        reqData = req.POST
        username = reqData.get('username')
        password = reqData.get('password')
        userlist = User.objects.filter(username=username)
        print("username="+username+"\tpassword="+password)
        data = {
            'flag':1,
        }
        if userlist.exists():
            '''，存先判断用户是否存在在就验证密码'''
            user = userlist[0]
            passwd = md5(password.encode('utf-8')).hexdigest();
            if user.password == passwd:
                '''获取当前时间，并且格式化'''
                last_login_time = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
                '''修改用户的最后登录时间并保存'''
                user.last_login_time = last_login_time
                user.save()
                # return HttpResponse("登陆成功")
                req.session['userId'] = user.id
                req.session['userName'] = user.username
                req.session['avatarUrl'] = IMGS_URL + user.avatarUrl
                req.session['email'] = user.email
                req.session['password'] = user.password
                a = req.session.get('userId')
                print("session="+str(a))
                return render(req,'index.html')
                # return render(req,'main.html')
            else:
                data['msg'] = '密码错误!'
                return render(req,'login.html',data)
        else:
            data['msg'] = '用户不存在!'

        return render(req,'login.html',data)

def getById(req):
    if req.method == 'POST':
        id = req.POST.get('id')
        print("id====",id)
        userlist = User.objects.filter(id=id)
        user = userlist[0]
        print("user===",user.username,user.avatarUrl,user.email,user.password)
        data = {
            "username":user.username,
            "avatarUrl":user.avatarUrl,
            "email":user.email,
            "password":user.password
        }

    return HttpResponse(json.dumps(data))

def update(req):
    if req.method == 'POST':
        reqData = req.POST
        data = {
            "status":500
        }
        username = reqData.get('username')
        id = reqData.get('id');
        # 头像地址传过来的是带请求路径的，需要把请求路径去掉
        avatarUrl = reqData.get('avatarUrl')
        last = avatarUrl.rfind('/')
        avatarSrc = avatarUrl[last:]

        email = reqData.get('email')
        password = reqData.get('password')
        repassword = reqData.get('repassword')
        repasswd = md5(repassword.encode('utf-8')).hexdigest();

        print(id, username, avatarUrl, email, password, repassword)

        # user = User.objects.get(id=id)

        if username == "":
            data['msg'] = '用户名不能为空'
            # return HttpResponse(json.dumps(data))
        elif email == "":
            data['msg'] = '邮箱不能为空'
            # return HttpResponse(json.dumps(data))
        elif password == "":
            data['msg'] = '密码不能为空'
            # return HttpResponse(json.dumps(data))
        elif repassword == "":
            data['msg'] = '确认密码不能为空'
            # return HttpResponse(json.dumps(data))
        elif password != repasswd:
            '''如果两次密码不一致不给修改'''
            data['msg'] = '两次密码不一致'
        else:
            # passwd = md5(password.encode('utf-8')).hexdigest();
            updateData = {
                "username": username,
                "avatarUrl": avatarSrc,
                "email": email,
                "password": password
            }
            User.objects.filter(id=id).update(**updateData)
            data['data'] = {
                "username":username,
                "avatarUrl": IMGS_URL + avatarSrc,
            }
            data['msg'] = "修改成功"
            data["status"] = 200
    return HttpResponse(json.dumps(data))
