from django.db import models

# Create your models here.
class User(models.Model):
    id = models.BigAutoField("用户id",primary_key=True)
    username = models.CharField("用户姓名",max_length=20)
    password = models.CharField("用户密码",max_length=30)
    email = models.CharField("用户电子邮件",max_length=200)
    avatarUrl = models.CharField("用户头像地址",max_length=255,default='/moren.jpg')
    creat_time = models.DateTimeField("创建时间",auto_now_add=True)
    last_login_time = models.DateTimeField("最后登陆时间")


