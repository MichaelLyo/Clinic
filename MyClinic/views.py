from django.shortcuts import render

# Create your views here.

import json
from django.http import HttpResponse
from .models import *
from django.core import serializers
from django.core.cache import cache
from . import tools
import traceback


def index(request):
    return HttpResponse("这是鲁明卫生室数据管理平台的后端！\nWelcome!\n您可以在网址后追加admin以进入后台管理页面\n本页面无其他作用")

def transform_validity(request):
    for item in Drug.objects.all():
        new_date = tools.transform_date(item.validity_period)
        item.validity_date = new_date if new_date else item.validity_date
        item.save()
    return HttpResponse("success")