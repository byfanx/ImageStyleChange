from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def hello(req):
    # print(id)
    cid = req.GET.get('cid')
    print(cid)
    aa = {"data":"lalala"}
    return render(req,"hello.html",aa)

def hello2(req):
    return HttpResponse('Hello,World!')
