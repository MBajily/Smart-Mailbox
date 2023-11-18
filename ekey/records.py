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

ttlock = TTLock(clientId, clientSecret)


@csrf_exempt
def records(request):
    auth_token = request.META.get('HTTP_USER_TOKEN')
    
    if auth_token is None:
        return HttpResponse(status=401)

    try:
        data = json.loads(request.body.decode('utf-8'))
        date = round(time.time()*1000)
        lockId = data.get('lockId')
        payload = {'clientId':clientId, 'accessToken':auth_token, 'lockId':lockId, 'date':date, 'pageNo':1, 'pageSize':100}
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        r = requests.get('https://euapi.ttlock.com/v3/lockRecord/list', headers=headers, params=payload)
        
        if "errcode" in (r.json()):
            return HttpResponse(r, status=401)

        return HttpResponse(r)

    except:
        return HttpResponse(status=401)



@csrf_exempt
def recordsCallback(request):
    if request.method == "POST":
        try:
            # data = json.loads(request.body.decode('utf-8'))
            lockId = request.POST.get('lockId')
            data = request.POST.get('records')
            print(data)
            data = json.loads(data)
            for record in data:
                print('record=', record)
                recordType = record.get('recordType')
                success = record.get('success')
                keyboardPwd = record.get('keyboardPwd')
                timestamp =  int(record.get('lockDate'))/1000
                lockDate = datetime.datetime.fromtimestamp(timestamp)

                notification = Notification(lockId=lockId, recordType=recordType, success=success, keyboardPwd=keyboardPwd, lockDate=lockDate)
                notification.save()

            response = {"success"} 
            return HttpResponse(response, status=200)

        except Exception as e:
            return HttpResponse(e, status=400)

    return HttpResponse(status=400)