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

ttlock = TTLock(clientId, clientSecret)

# Create your views here.
def register(request):
    if request.method == 'POST':
        formset = RegisterForm(request.POST)
        if formset.is_valid():
            formset.save()
            email = request.POST['email']
            password = request.POST['password1']
            username = str(email.split('@')[0])
            hashed_password = hashlib.md5(password.encode()).hexdigest()
            new_user = ttlock.create_user(clientId=clientId, clientSecret=clientSecret, username=username, password=hashed_password)
            access_token = ttlock.get_token(clientId=clientId, clientSecret=clientSecret, username=new_user['username'], password=hashed_password, redirect_uri='')
            # print('access_token == ',access_token)
            selected_client = User.objects.filter(email=email)
            selected_client.update(username=username, ttlock_username = 'cfbge_' + username,
                                    hashed_password=hashed_password, access_token=access_token['access_token'])
            return redirect('locksList')
    else:
        formset = RegisterForm()

    context = {'title':'Sign up', 'formset':formset}

    return render(request, "ekey/registration.html", context)


def listLock(request):
    user = request.user
    
    date = round(time.time()*1000)

    payload = {'clientId':clientId, 'accessToken':user.access_token, 'date':date, 'pageNo':1, 'pageSize':20}
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    r = requests.get('https://cnapi.ttlock.com/v3/lock/list', headers=headers, params=payload)
    return HttpResponse(r)


# def randomPasscode(request):
#     user = request.user
    
#     date = round(time.time()*1000)

#     payload = {
#                 'clientId':clientId, 'accessToken':user.access_token, 
#                 'date':date, 'startDate':date,
#                 'lockId':24451, 'keyboardPwdType':1,
#                 }
#     headers = {'Content-Type': 'application/x-www-form-urlencoded'}
#     r = requests.post('https://cnapi.ttlock.com/v3/lock/initialize', headers=headers, params=payload)
#     return HttpResponse(r)


def lockDetails(request, lock_id):
    user = request.user
    date = round(time.time()*1000)

    payload = {'clientId':clientId, 'accessToken':user.access_token, 'date':date, 'lockId':lock_id}
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    r = requests.get('https://cnapi.ttlock.com/v3/lock/detail', headers=headers, params=payload)
    return HttpResponse(r)


def getPasscode(request, lock_id, type_id):
    user = request.user
    normalFormatDate = time.time()
    print(normalFormatDate)
    date = round(normalFormatDate*1000)

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


def deletePasscode(request, lock_id, passcode_id):
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


def listPasscode(request, lock_id):
    user = request.user
    date = round(time.time()*1000)

    payload = {'clientId':clientId, 'accessToken':user.access_token, 'lockId':lock_id, 'pageNo':1, 'pageSize':100, 'date':date}
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    r = requests.get('https://cnapi.ttlock.com/v3/lock/listKeyboardPwd', headers=headers, params=payload)
    return HttpResponse(r)