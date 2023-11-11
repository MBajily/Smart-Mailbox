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


'''
    Request URL:
    'lock/{lock_id}/passcode/list/'

    Request parameters:
    - Lock ID

    Response:
    - keyboardPwdId
    - keyboardPwd : passcode number
    - keyboardPwdName : pascode name
    - sendDate : generate date
'''
@csrf_exempt
def passcodeList(request):
    auth_token = request.META.get('HTTP_USER_TOKEN')
    if auth_token is None:
        return HttpResponse(status=401)

    try:
        date = round(time.time()*1000)
        data = json.loads(request.body.decode('utf-8'))
        lockId = data.get('lockId')

        payload = {'clientId':clientId, 'accessToken':auth_token, 'lockId':lockId, 'pageNo':1, 'pageSize':100, 'date':date}
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        r = requests.get('https://cnapi.ttlock.com/v3/lock/listKeyboardPwd', headers=headers, params=payload)
        if "errcode" in (r.json()):
                return HttpResponse(status=401)

        return HttpResponse(r)

    except:
        return HttpResponse(status=401)


'''
    Request URL:
    'lock/{lock_id}/passcode/{type_id}/new/'

    Request parameters:
    - Lock ID
    - Type ID (1: one-time, 2: permanent)

    Response:
    - keyboardPwdId : passcode id
    - keyboardPwd : passcode number
'''
@csrf_exempt
def passcodeNew(request):
    if request.method == "POST":
        auth_token = request.META.get('HTTP_USER_TOKEN')
        if auth_token is None:
            return HttpResponse(status=401)

        try:
            date = round(time.time()*1000)
            data = json.loads(request.body.decode('utf-8'))
            lockId = data.get('lockId')
            passcodeType = data.get('passcodeType')

            payload = {'clientId':clientId, 'accessToken':auth_token, 'lockId':lockId, 'keyboardPwdType':int(passcodeType), 'startDate':date, 'date':date}
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            r = requests.get('https://cnapi.ttlock.com/v3/keyboardPwd/get', headers=headers, params=payload)
            
            if "errcode" in (r.json()):
                return HttpResponse(status=401)

            # print(r.status_code, r.json()["keyboardPwdId"])
            return HttpResponse(r)

        except:
            return HttpResponse(status=401)

    return HttpResponse(status=400)


'''
    Request URL:
    'lock/<str:lock_id>/passcode/<str:passcode_id>/update/<str:passcode>/'

    Request parameters:
    - Lock ID
    - Passcode ID
    - New Passcode

    Response:
    - errorcode
    - errormessage
'''
@csrf_exempt
def passcodeUpdate(request):
    if request.method == "POST":
        auth_token = request.META.get('HTTP_USER_TOKEN')
        if auth_token is None:
            return HttpResponse(status=401)

        try:
            date = round(time.time()*1000)
            data = json.loads(request.body.decode('utf-8'))
            lockId = data.get('lockId')
            passcodeId = data.get('passcodeId')
            passcodeName = data.get('passcodeName')
            passcode = data.get('passcode')

            payload = {'clientId':clientId, 'accessToken':auth_token,
                        'lockId':lockId, 'keyboardPwdId':passcodeId,
                        'keyboardPwdName':passcodeName, 'newKeyboardPwd':passcode,
                        'date':date}
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            r = requests.post('https://cnapi.ttlock.com/v3/keyboardPwd/change', headers=headers, params=payload)
            if (r.json())["errcode"] != 0:
                return HttpResponse(status=401)

            return HttpResponse(status=200)

        except:
            return HttpResponse(status=401)

    return HttpResponse(status=400)


'''
    Request URL:
    'lock/<str:lock_id>/passcode/<str:passcode_id>/delete/'

    Request parameters:
    - Lock ID
    - Passcode ID

    Response:
    - errorcode
    - errormessage
'''
@csrf_exempt
def passcodeDelete(request):
    if request.method == "POST":
        auth_token = request.META.get('HTTP_USER_TOKEN')
        if auth_token is None:
            return HttpResponse(status=401)

        try:
            date = round(time.time()*1000)
            data = json.loads(request.body.decode('utf-8'))
            lockId = data.get('lockId')
            passcodeId = data.get('passcodeId')

            payload = {'clientId':clientId, 'accessToken':auth_token, 'lockId':lockId, 'keyboardPwdId':passcodeId, 'date':date}
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            r = requests.post('https://cnapi.ttlock.com/v3/keyboardPwd/delete', headers=headers, params=payload)

            if (r.json())["errcode"] != 0:
                return HttpResponse(status=401)

            return HttpResponse(status=200)

        except:
            return HttpResponse(status=401)

    return HttpResponse(status=400)


