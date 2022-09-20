"""ImageStyleChange URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from userApp import views as uv
from imgsApp import views as iv

urlpatterns = [
    path('admin/', admin.site.urls),
    path('hello/', uv.hello),
    path('',uv.index),
    path('register', uv.register),
    path('login',uv.login),
    path('getById',uv.getById),
    path('update',uv.update),
    path('upload',iv.upload),
    path('download',iv.download),
    path('original',iv.original),
    path('sketch',iv.sketch),
    path('LineDraft',iv.LineDraft),
    path('cartoon',iv.cartoon),
    path('gray',iv.gray),
    path('xFlip',iv.xFlip),
    path('yFlip',iv.yFlip),
    path('centre',iv.centre),
    path('strimg',iv.strimg),
    path('strimgColor',iv.strimgColor),
    path('emboss',iv.emboss),
    path('dipian',iv.dipian),
    path('transfer',iv.transfer),
]
