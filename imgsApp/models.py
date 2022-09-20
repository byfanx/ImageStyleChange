import os

from django.db import models
# Create your models here.

class Image(models.Model):
    id = models.BigAutoField("图片id", primary_key=True)
    user_id = models.IntegerField("用户id")
    img_url = models.CharField("图片名称", max_length=255)
    width = models.IntegerField("图片高度")
    height = models.IntegerField("图片宽度")
    creat_time = models.DateTimeField("上传时间", auto_now_add=True)


    '''
    # upload_to 参数接收一个回调函数 user_directory_path，该函数返回具体的路径字符串，图片会自动上传到指定路径下，即 MEDIA_ROOT + upload_to
    # user_directory_path 函数必须接收 instace 和 filename 两个参数。参数 instace 代表一个定义了 ImageField 的模型的实例，说白了就是当前数据记录；filename 是原本的文件名
    # null 是针对数据库而言，如果 null = True, 表示数据库的该字段可以为空；blank 是针对表单的，如果 blank = True，表示你的表单填写该字段的时候可以不填，但是对数据库来说，没有任何影响
    '''
    # img_url = models.ImageField("原始图片",upload_to=user_directory_path,blank=True,null=True,max_length=255)



