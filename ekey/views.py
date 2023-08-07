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


def locksList(request):
    user = request.user
    
    date = round(time.time()*1000)

    payload = {'clientId':clientId, 'accessToken':user.access_token, 'date':date, 'pageNo':1, 'pageSize':20}
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    r = requests.get('https://cnapi.ttlock.com/v3/lock/list', headers=headers, params=payload)
    return HttpResponse(r)


def randomPasscode(request):
    user = request.user
    
    date = round(time.time()*1000)

    payload = {
                'clientId':clientId, 'accessToken':user.access_token, 
                'date':date, 'startDate':date,
                'lockId':24451, 'keyboardPwdType':1,
                }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    r = requests.post('https://cnapi.ttlock.com/v3/lock/initialize', headers=headers, params=payload)
    return HttpResponse(r)


def lockDetails(request, lock_id):
    user = request.user
    date = round(time.time()*1000)

    payload = {'clientId':clientId, 'accessToken':user.access_token, 'date':date, 'lockId':lock_id}
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    r = requests.get('https://cnapi.ttlock.com/v3/lock/detail', headers=headers, params=payload)
    return HttpResponse(r)
