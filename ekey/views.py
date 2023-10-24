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
from django.contrib.auth import authenticate, login, logout
from django.contrib.sessions.backends.db import SessionStore
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

load_dotenv()

clientId = os.getenv("CLIENT_ID")
clientSecret = os.getenv('CLIENT_SECRET')

ttlock = TTLock(clientId, clientSecret)


def get_session_id(request):
    session_cookie_name = settings.SESSION_COOKIE_NAME
    session_id = request.COOKIES.get(session_cookie_name)
    return session_id

def getUser(request):
    from django.contrib.auth.models import AnonymousUser
    try:
        user_id = request.session.session_key
        backend_path = request.session.backend_session_key
        backend = load_backend(backend_path)
        user = backend.get_user(user_id) or AnonymousUser()
    except KeyError:
        user = AnonymousUser()
    return user


@csrf_exempt
def register(request):
    if request.method == 'POST':
        formset = RegisterForm(request.POST)
        if formset.is_valid():
            formset.save()
            email = request.POST['email']
            username = request.POST['username']
            password = request.POST['password1']
            hashed_password = hashlib.md5(password.encode()).hexdigest()
            selected_client = User.objects.filter(email=email)
            try:
                new_user = ttlock.create_user(clientId=clientId, clientSecret=clientSecret, username=username, password=hashed_password)
                access_token = ttlock.get_token(clientId=clientId, clientSecret=clientSecret, username=new_user['username'], password=hashed_password, redirect_uri='')
                print(new_user)
                selected_client.update(ttlock_username = new_user['username'], hashed_password=hashed_password,
                                        access_token=access_token['access_token'])
                return redirect('login') #done
                
            except:
                selected_client.delete()
                return redirect('register')

            return redirect('register')
            
    else:
        formset = RegisterForm()

    context = {'title':'Sign up', 'formset':formset}

    return render(request, "ekey/registration.html", context)


@csrf_exempt
def loginUser(request):
    form = LoginForm()
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, email=email, password=password)
        print('user=', user)
        if user is not None:
            login(request, user)
            # Save the session to get the session ID
            request.session.save()
            session_id = request.session.session_key
            print('request.user=', request.user)
            accessToken(request) # Done
            return redirect('lockList')
        else:
            return redirect('login')

    context = {'title':'Login', 'form':form}
    return render(request, "registration/login.html", context)



def logoutUser(request):
    logout(request)
    return redirect('login')


# Done
def accessToken(request):
    user = getUser(request)
    access_token = ttlock.get_token(clientId=clientId, clientSecret=clientSecret, username=user.ttlock_username, password=user.hashed_password, redirect_uri='')
    access_token = access_token["access_token"]
    if (user.access_token is None) or (user.access_token == '') or (user.access_token != access_token):
        # payload = {'clientId':clientId, 'clientSecret':clientSecret, 'username':user.ttlock_username, 'password':user.hashed_password}
        # headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        # r = requests.post('https://cnapi.ttlock.com/oauth2/token', headers=headers, params=payload)
        selectedUser = User.objects.filter(email=user.email)
        selectedUser.update(access_token=access_token)
    
    return HttpResponse(user.access_token)


def lockList(request):
    user = getUser(request)
    print('user2 =', user)
    date = round(time.time()*1000)

    payload = {'clientId':clientId, 'accessToken':user.access_token, 'date':date, 'pageNo':1, 'pageSize':20}
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    r = requests.get('https://cnapi.ttlock.com/v3/lock/list', headers=headers, params=payload)
    return HttpResponse(r)


def lockDetails(request, lock_id):
    user = getUser(request)
    date = round(time.time()*1000)

    payload = {'clientId':clientId, 'accessToken':user.access_token, 'date':date, 'lockId':lock_id}
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    r = requests.get('https://cnapi.ttlock.com/v3/lock/detail', headers=headers, params=payload)
    return HttpResponse(r)


def lockDelete(request, lock_id):
    user = getUser(request)
    date = round(time.time()*1000)

    payload = {'clientId':clientId, 'accessToken':user.access_token, 'date':date, 'lockId':lock_id}
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    r = requests.get('https://cnapi.ttlock.com/v3/lock/delete', headers=headers, params=payload)
    return HttpResponse(r)
