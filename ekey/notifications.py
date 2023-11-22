import os
import hashlib
import requests
import datetime
import time
import json
from django.shortcuts import render, redirect
from ttlockwrapper import TTLock
from dotenv import load_dotenv
from api.models import *
from .forms import *
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt


load_dotenv()

clientId = os.getenv("CLIENT_ID")
clientSecret = os.getenv('CLIENT_SECRET')

# with open('/etc/config.json') as config_file:
#     config = json.load(config_file)

# clientId = config["CLIENT_ID"]
# clientSecret = config["CLIENT_SECRET"]


@csrf_exempt
def notifications(request):
    auth_token = request.META.get('HTTP_USER_TOKEN')
    
    if auth_token is None:
        return HttpResponse(status=401)

    try:
        selectedUser = User.objects.get(access_token=auth_token)
        notifications = Notification.objects.filter(receiver=selectedUser).all()
        result = []

        for notification in notifications:
            item = {}
            item["subject"] = notification.subject
            item["message"] = notification.message
            item["date"] = str(notification.date)[:19]

            result.append(item)

        return HttpResponse(json.dumps(result))

    except Exception as e:
        return HttpResponse(e, status=400)

    return HttpResponse(status=400)


    