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
            payload = {'clientId':clientId, 'accessToken':auth_token, 'lockData':lockData, 'date':date}
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            r = requests.post('https://cnapi.ttlock.com/v3/lock/initialize', headers=headers, params=payload)
        
            if "errcode" in (r.json()):
                return HttpResponse(r, status=401)

            print(r.json()["lockId"])
            lockAutoLock(request, auth_token, lockId=r.json()["lockId"])
        
            return HttpResponse(r)
        
        except Exception as e:
            return HttpResponse(e, status=401)

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

        r = r.json()
        result = {"list":[]}

        for lock in r["list"]:
            lockId = lock["lockId"]
            selectedLocation = Location.objects.filter(lock_id=lockId).last()
            if selectedLocation:
                lock["location"] = {
                    "latitude": float(selectedLocation.latitude),
                    "longitude": float(selectedLocation.longitude)}
            else:
                lock["location"] = None

            lock["lockSound"] = lockSound(request, auth_token, lockId)

            result["list"].append(lock)


        result = json.dumps(result)
        
        return HttpResponse(result)

    except Exception as e:
        return HttpResponse(e, status=401)

    return HttpResponse(status=401)


def lockSound(request, auth_token, lockId):
    if auth_token is None:
        return HttpResponse(status=401)

    # user = request.user
    date = round(time.time()*1000)
    payload = {'clientId':clientId, 'accessToken':auth_token, 'date':date, 'lockId':lockId}
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    r = requests.get('https://cnapi.ttlock.com/v3/lock/detail', headers=headers, params=payload)
    r = r.json()
    return r["lockSound"]


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

        r = r.json()
        selectedLocation = Location.objects.filter(lock_id=lockId).last()
        if selectedLocation:
            r["location"] = {
                "latitude": float(selectedLocation.latitude),
                "longitude": float(selectedLocation.longitude)}
        else:
            r["location"] = None

        r = json.dumps(r)
        return HttpResponse(r, content_type='application/json')

    except Exception as e:
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



def lockAutoLock(request, auth_token, lockId):        
    if auth_token is None:
        return HttpResponse("999999", status=401)

    try:
        date = round(time.time()*1000)

        payload = {'clientId':clientId, 'accessToken':auth_token, 'lockId':lockId, 'seconds':5, 'type':1, 'date':date}
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        req = requests.post('https://euapi.ttlock.com/v3/lock/setAutoLockTime', headers=headers, params=payload)
        
        if (req.json())["errcode"] != 0:
            return HttpResponse(status=401)
        print(req)

    except Exception as e:
        return HttpResponse(e, status=401)

