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
        
        r_json = r.json()["list"]

        result = []

        for record in r_json:
            element = {
                "recordType":record["recordType"],
                }
            record_type = record["recordType"]
            if record_type == 1:
                element["message"] = "تم فتح الصندوق باستخدام التطبيق"
            
            elif record_type == 4:
                if record["success"] == 1:
                    element["message"] = "تم فتح الصندوق باستخدام الكود " + "(***" + record["keyboardPwd"][:5] + ")"
                else:
                    element["message"] = "محاولة فاشلة لفتح الصندوق بالكود " + "(***" + record["keyboardPwd"][:5] + ")"

            elif record_type == 48:
                element["message"] = "تحذير! تم اكتشاف محاولات وصول غير مصرح بها"
            
            elif record_type == 11:
                element["message"] = "تم إغلاق الصندوق بنجاح"

            elif record_type == 45:
                element["message"] = "تم إغلاق الصندوق بنجاح (تلقائيا)"

            elif record_type == 10:
                element["message"] = "تم فتح الصندوق باستخدام المفتاح اليدوي"
            
            timestamp =  int(record["lockDate"])/1000
            recordDate = datetime.datetime.fromtimestamp(timestamp)
            element["date"] = str(recordDate)
            result.append(element)

        return HttpResponse(json.dumps(result))

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

                record = Record(lockId=lockId, recordType=recordType, success=success, keyboardPwd=keyboardPwd, lockDate=lockDate)
                record.save()

            response = {"success"} 
            return HttpResponse(response, status=200)

        except Exception as e:
            return HttpResponse(e, status=400)

    return HttpResponse(status=400)