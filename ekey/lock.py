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

# load_dotenv()

# clientId = os.getenv("CLIENT_ID")
# clientSecret = os.getenv('CLIENT_SECRET')

with open('/etc/config.json') as config_file:
    config = json.load(config_file)

clientId = config["CLIENT_ID"]
clientSecret = config["CLIENT_SECRET"]

ttlock = TTLock(clientId, clientSecret)


'''
    Request URL:
    https://api.sahlbox.com/lock/list/

    Request Method: GET

    Request parameters:
    - No require

    Response:
    - 200 OK
        Parameter:
        - list (JSONArray):
            - lockId
            - lockName
        - pageNo
        - pageSize
        - pages
        - total
    - 400 Bad Request -> Redirect to login page
'''
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

'''
    Request URL:
    https://api.sahlbox.com/lock/details/

    Request Method: GET

    Request parameters:
    - lockId

    Response:
    - 200 OK
        Parameter:
        - lockId
        - lockName
        - lockMac
        - lockSound (0-unknow, 1-on, 2-off)
    
    or
    - 400 Bad Request -> Stay in same page
'''
@csrf_exempt
def lockDetails(request):
    auth_token = request.META.get('HTTP_USER_TOKEN')
    if auth_token is None:
        return HttpResponse(status=401)

    try:
        # user = request.user
        date = round(time.time()*1000)
        lockId = request.GET.get('lockId', '')
        payload = {'clientId':clientId, 'accessToken':auth_token, 'date':date, 'lockId':lockId}
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        r = requests.get('https://cnapi.ttlock.com/v3/lock/detail', headers=headers, params=payload)
        
        if "errcode" in (r.json()):
            return HttpResponse(status=401)

        return HttpResponse(r)

    except:
        return HttpResponse(status=401)

    return HttpResponse(status=401)


'''
    Request URL:
    https://api.sahlbox.com/lock/<str:lock_id>/details/

    Request Method: POST

    Request parameters:
    - lock_id

    Response:
    - 200 OK.
    - 400 Bad Request.
'''
@csrf_exempt
def lockDelete(request):
    if request.method == 'POST':
        auth_token = request.META.get('HTTP_USER_TOKEN')
        
        if auth_token is None:
            return HttpResponse(status=401)
        
        try:
            # user = request.user
            date = round(time.time()*1000)
            lockId = request.GET.get("lockId")
            payload = {'clientId':clientId, 'accessToken':auth_token, 'date':date, 'lockId':int(lockId)}
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            r = requests.get('https://cnapi.ttlock.com/v3/lock/delete', headers=headers, params=payload)
            
            if (r.json())["errcode"] != 0:
                return HttpResponse(status=401)
            
            return HttpResponse(status=200)
        
        except:
            return HttpResponse(status=401)

    return HttpResponse(status=401)


'''
    Request URL:
    https://api.sahlbox.com/lock/name/update/

    Request Method: POST

    Request parameters:
    - lockId
    - lockAlias

    Response:
    - 200 OK.
    - 400 Bad Request.
'''
@csrf_exempt
def lockNameUpdate(request):
    date = round(time.time()*1000)
    # user = request.user
    if request.method == 'POST':
        auth_token = request.META.get('HTTP_USER_TOKEN')
        
        if auth_token is None:
            return HttpResponse(status=401)
        
        try:
            lockId = request.GET.get('lockId')
            lockAlias = request.GET.get("lockAlias")
            payload = {'clientId':clientId, 'accessToken':auth_token, 'lockId':lockId, 'lockAlias':lockAlias, 'date':date}
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            r = requests.post('https://cnapi.ttlock.com/v3/lock/rename', headers=headers, params=payload)
        
            if (r.json())["errcode"] != 0:
                return HttpResponse(status=401)
        
            return HttpResponse(status=200)
        
        except:
            return HttpResponse(status=401)

    return HttpResponse(status=401)

