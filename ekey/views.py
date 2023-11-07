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
    https://api.sahlbox.com/register/

    Request Method: POST

    Request parameters:
    - username
    - email
    - full_name
    - phone
    - gender (1- Mail, 2- Femail, 3- Prefer not to say)
    - birth_date
    - password

    Response:
    - 200 OK -> Redirect to login page.
    - 400 Bad Request -> Should redirect to register page and tell the user: “invalid registration details”.
'''
def register(request):
    if request.method == 'POST':
        # formset = RegisterForm(request.POST)
        try:
            formset = User.objects.create(email = request.POST['email'],
                username = request.POST['username'],
                password = request.POST['password'])
            if formset:
                formset.save()
                email = request.POST['email']
                username = request.POST['username']
                password = request.POST['password']
                hashed_password = hashlib.md5(password.encode()).hexdigest()
                selected_client = User.objects.filter(email=email)
                new_user = ttlock.create_user(clientId=clientId, clientSecret=clientSecret, username=username, password=hashed_password)
                try:
                    access_token = ttlock.get_token(clientId=clientId, clientSecret=clientSecret, username=new_user['username'], password=hashed_password, redirect_uri='')
                    # print(selected_client)
                    selected_client.update(ttlock_username=new_user['username'], hashed_password=hashed_password,
                                            access_token=access_token['access_token'])
                    # print(selected_client)
                    selectedProfile = UserProfile.objects.filter(user__in=selected_client).first()
                    selectedProfile.full_name = request.POST['full_name']
                    selectedProfile.phone = request.POST['phone']
                    selectedProfile.birth_date = request.POST['birth_date']
                    selectedProfile.gender = request.POST['gender']
                    # print(selectedProfile)
                    if selectedProfile:
                        selectedProfile.save()
                        result = {}
                        result["USER_TOKEN"] = access_token['access_token']
                        return HttpResponse(json.dumps(result), status=200)
                    
                except Exception as e:
                    date = round(time.time()*1000)
                    # print(new_user['username'])
                    payload = {'clientId':clientId, 'clientSecret':clientSecret, 'date':date, 'username':new_user['username']}
                    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
                    requests.post('https://euapi.ttlock.com/v3/user/delete', headers=headers, params=payload)
                    selected_client.delete()
                    # print(e)
                    # return redirect('register')
                    return HttpResponse(e)

                finally:
                    return HttpResponse(status=400)


        except Exception as e:
            print(e)
            # return redirect('register')
            return HttpResponse(e)
                
        # return redirect('register')
        finally:
            return HttpResponse(status=400)
            
    else:
        formset = RegisterForm()

    context = {'title':'Sign up', 'formset':formset}

    return render(request, "ekey/registration.html", context)


'''
    Request URL:
    https://api.sahlbox.com/login/

    Request Method: POST

    Request parameters:
    - email
    - password

    Response:
    - 200 OK -> Redirect to home page.
    - 400 Bad Request -> Should redirect to login page and tell the user “The email or password is wrong”.
'''
def loginUser(request):
    form = LoginForm()
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            access_token = accessToken(request) # Done
            # return redirect('lockList')
            # return HttpResponse(status=200)
            result = {}
            result["USER_TOKEN"] = access_token
            return HttpResponse(json.dumps(result), status=200)
        else:
            # return redirect('login')
            return HttpResponse(status=400)

    context = {'title':'Login', 'form':form}
    return render(request, "registration/login.html", context)


'''
    Request URL:
    https://api.sahlbox.com/logout/

    Request Method: GET

    Request parameters:
    - Not require

    Response:
    - 200 OK -> Redirect to login page.
    - 400 Bad Request -> Stay in same page.
'''
def logoutUser(request):
    try:
        logout(request)
        # return redirect('login')
        return HttpResponse(status=200)
    except:
        return HttpResponse(status=400)


# Done
def accessToken(request):
    user = request.user
    access_token = ttlock.get_token(clientId=clientId, clientSecret=clientSecret, username=user.ttlock_username, password=user.hashed_password, redirect_uri='')
    access_token = access_token["access_token"]
    if (user.access_token is None) or (user.access_token == '') or (user.access_token != access_token):
        # payload = {'clientId':clientId, 'clientSecret':clientSecret, 'username':user.ttlock_username, 'password':user.hashed_password}
        # headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        # r = requests.post('https://cnapi.ttlock.com/oauth2/token', headers=headers, params=payload)
        selectedUser = User.objects.filter(email=user.email)
        selectedUser.update(access_token=access_token)
    
    return user.access_token

