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
from django.http import HttpResponse, JsonResponse
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
def lockInit(request):
    if request.method == 'POST':
        auth_token = request.META.get('HTTP_USER_TOKEN')
        
        if auth_token is None:
            return HttpResponse(status=401)
        
        try:
            date = round(time.time()*1000)
            data = json.loads(request.body.decode('utf-8'))
            lockData = data.get('lockData')
            print("lockData =",lockData)
            payload = {'clientId':clientId, 'accessToken':auth_token, 'lockData':lockData, 'date':date}
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            r = requests.post('https://cnapi.ttlock.com/v3/lock/initialize', headers=headers, params=payload)
        
            if "errcode" in (r.json()):
                return HttpResponse(r, status=401)
        
            return HttpResponse(r)
        
        except:
            return HttpResponse(status=401)

    return HttpResponse(status=401)


@csrf_exempt
def lockList(request):
    auth_token = request.META.get('HTTP_USER_TOKEN')
    
    if auth_token is None:
        return HttpResponse(status=401)

    try:
        # user = request.user
        date = round(time.time()*1000)
        payload = {'clientId':clientId, 'accessToken':auth_token, 'date':date, 'pageNo':1, 'pageSize':100}
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        r = requests.get('https://cnapi.ttlock.com/v3/lock/list', headers=headers, params=payload)
        
        if "errcode" in (r.json()):
            return HttpResponse(status=401)
        
        return HttpResponse(r)

    except:
        redirect('logout')
        return HttpResponse(status=401)

    return HttpResponse(status=401)


@csrf_exempt
def lockDetails(request):
    auth_token = request.META.get('HTTP_USER_TOKEN')
    if auth_token is None:
        return HttpResponse(status=401)

    try:
        # user = request.user
        date = round(time.time()*1000)
        data = json.loads(request.body.decode('utf-8'))
        lockId = data.get('lockId')
        payload = {'clientId':clientId, 'accessToken':auth_token, 'date':date, 'lockId':lockId}
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        r = requests.get('https://cnapi.ttlock.com/v3/lock/detail', headers=headers, params=payload)
        
        if "errcode" in (r.json()):
            return HttpResponse(status=401)

        return HttpResponse(r)

    except:
        return HttpResponse(status=401)

    return HttpResponse(status=401)


@csrf_exempt
def lockDelete(request):
    if request.method == 'POST':
        auth_token = request.META.get('HTTP_USER_TOKEN')
        
        if auth_token is None:
            return HttpResponse(status=401)
        
        try:
            # user = request.user
            date = round(time.time()*1000)
            data = json.loads(request.body.decode('utf-8'))
            lockId = data.get("lockId")
            payload = {'clientId':clientId, 'accessToken':auth_token, 'date':date, 'lockId':int(lockId)}
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            r = requests.get('https://cnapi.ttlock.com/v3/lock/delete', headers=headers, params=payload)
            
            if (r.json())["errcode"] != 0:
                return HttpResponse(status=401)
            
            return HttpResponse(status=200)
        
        except:
            return HttpResponse(status=401)

    return HttpResponse(status=401)


@csrf_exempt
def lockNameUpdate(request):
    if request.method == 'POST':
        date = round(time.time()*1000)
        auth_token = request.META.get('HTTP_USER_TOKEN')
        
        if auth_token is None:
            return HttpResponse(status=401)
        
        try:
            data = json.loads(request.body.decode('utf-8'))
            lockId = data.get('lockId')
            lockAlias = data.get("lockAlias")
            payload = {'clientId':clientId, 'accessToken':auth_token, 'lockId':lockId, 'lockAlias':lockAlias, 'date':date}
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            r = requests.post('https://cnapi.ttlock.com/v3/lock/rename', headers=headers, params=payload)
        
            if (r.json())["errcode"] != 0:
                return HttpResponse(status=401)
        
            return HttpResponse(status=200)
        
        except:
            return HttpResponse(status=401)

    return HttpResponse(status=401)


@csrf_exempt
def lockSoundUpdate(request):
    if request.method == 'POST':
        auth_token = request.META.get('HTTP_USER_TOKEN')
        
        if auth_token is None:
            return HttpResponse(status=401)

        try:
            date = round(time.time()*1000)
            data = json.loads(request.body.decode('utf-8'))
            lockId = data.get('lockId')
            value = data.get('sound')

            payload = {'clientId':clientId, 'accessToken':auth_token, 'lockId':lockId, 'type':6, 'value':value, 'date':date}
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            r = requests.post('https://euapi.ttlock.com/v3/lock/updateSetting', headers=headers, params=payload)
            
            if (r.json())["errcode"] != 0:
                return HttpResponse(status=401)

            return JsonResponse({"sound":value})

        except Exception as e:
            return HttpResponse(status=401)

    return HttpResponse(status=401)


@csrf_exempt
def lockAutoLock(request):
    if request.method == 'POST':
        auth_token = request.META.get('HTTP_USER_TOKEN')
        
        if auth_token is None:
            return HttpResponse(status=401)

        try:
            date = round(time.time()*1000)
            data = json.loads(request.body.decode('utf-8'))
            lockId = data.get('lockId')
            value = data.get('sound')

            payload = {'clientId':clientId, 'accessToken':auth_token, 'lockId':lockId, 'seconds':5, 'type':2, 'date':date}
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            r = requests.post('https://euapi.ttlock.com/v3/lock/setAutoLockTime', headers=headers, params=payload)
            
            if (r.json())["errcode"] != 0:
                return HttpResponse(status=401)

            return HttpResponse(status=200)

        except Exception as e:
            return HttpResponse(status=401)

    return HttpResponse(status=401)
