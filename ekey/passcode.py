import os
import hashlib
import requests
import datetime
import time
from django.shortcuts import render, redirect
from ttlockwrapper import TTLock
from dotenv import load_dotenv
from api.models import *
from .forms import *
from django.http import HttpResponse


load_dotenv()

clientId = os.getenv("CLIENT_ID")
clientSecret = os.getenv('CLIENT_SECRET')


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
def passcodeNew(request, lock_id, type_id):
    user = request.user
    date = round(time.time()*1000)

    payload = {'clientId':clientId, 'accessToken':user.access_token, 'date':date, 'lockId':lock_id, 'keyboardPwdType':int(type_id), 'startDate':date}
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    r = requests.get('https://cnapi.ttlock.com/v3/keyboardPwd/get', headers=headers, params=payload)
    if r.status_code == 200:
        responseData = r.json()
        newPasscode = Passcode(passcode_id=responseData["keyboardPwdId"], passcode=responseData["keyboardPwd"],
                                type=type_id)
        newPasscode.save()
    # print(r.status_code, r.json()["keyboardPwdId"])
    return HttpResponse(r)


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
def passcodeDelete(request, lock_id, passcode_id):
    user = request.user
    date = round(time.time()*1000)

    payload = {'clientId':clientId, 'accessToken':user.access_token, 'lockId':lock_id, 'keyboardPwdId':passcode_id, 'date':date}
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    r = requests.post('https://cnapi.ttlock.com/v3/keyboardPwd/delete', headers=headers, params=payload)
    if r.status_code == 200:
        responseData = r.json()

        selectedPasscode = Passcode.objects.get(passcode_id=passcode_id)
        if selectedPasscode:
            selectedPasscode.delete()
    return HttpResponse(r)


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
def passcodeList(request, lock_id):
    user = request.user
    date = round(time.time()*1000)

    payload = {'clientId':clientId, 'accessToken':user.access_token, 'lockId':lock_id, 'pageNo':1, 'pageSize':100, 'date':date}
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    r = requests.get('https://cnapi.ttlock.com/v3/lock/listKeyboardPwd', headers=headers, params=payload)
    return HttpResponse(r)


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
def passcodeUpdate(request,lock_id, passcode_id, passcode):
    date = round(time.time()*1000)
    user = request.user
    payload = {'clientId':clientId, 'accessToken':user.access_token, 'lockId':lock_id, 'keyboardPwdId':passcode_id, 'newKeyboardPwd':passcode, 'date':date}
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    if int(passcode):

        r = requests.post('https://cnapi.ttlock.com/v3/keyboardPwd/change', headers=headers, params=payload)
        return HttpResponse(r)

    return HttpResponse("Write a valid passcode using numbers!")