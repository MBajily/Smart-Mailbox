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
from django.views.decorators.csrf import csrf_exempt
from passlib.hash import django_pbkdf2_sha256 as handler
from django.contrib.auth.forms import PasswordResetForm
from django.conf import settings


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
@csrf_exempt
def register(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        try:
            email = data.get('email')
            username = data.get('username')
            password = data.get('password')
            request_body = {}

            if is_email_exists(email) and is_username_exists(username):
                request_body["errors"] = []
                request_body["errors"].append({"error": {"code": 1001, "message": "Username already exists"}})
                request_body["errors"].append({"error": {"code": 1002, "message": "Email already exists"}})
                return HttpResponse(json.dumps(request_body), status=400)

            if is_email_exists(email) or is_username_exists(username):
                request_body["errors"] = []
                if is_username_exists(username):
                    request_body["errors"].append({"error": {"code": 1001, "message": "Username already exists"}})

                if is_email_exists(email):
                    request_body["errors"].append({"error": {"code": 1002, "message": "Email already exists"}})

                return HttpResponse(json.dumps(request_body), status=400)

            formset = User.objects.create(email = email,
                username = username,
                password = handler.hash(password))
            if formset:
                formset.save()
                hashed_password = hashlib.md5(password.encode()).hexdigest()
                selected_client = User.objects.filter(email=email)
                new_user = ttlock.create_user(clientId=clientId, clientSecret=clientSecret, username=username, password=hashed_password)
                try:
                    access_token = ttlock.get_token(clientId=clientId, clientSecret=clientSecret, username=new_user['username'], password=hashed_password, redirect_uri='')
                    selected_client.update(ttlock_username=new_user['username'], hashed_password=hashed_password,
                                            access_token=access_token['access_token'])
                    selectedProfile = UserProfile.objects.filter(user__in=selected_client).first()
                    selectedProfile.full_name = data.get('full_name')
                    selectedProfile.phone = data.get('phone')
                    selectedProfile.birth_date = data.get('birth_date')
                    selectedProfile.gender = data.get('gender')
                    if selectedProfile:
                        selectedProfile.save()
                        result = {}
                        result["USER_TOKEN"] = access_token['access_token']
                        return HttpResponse(json.dumps(result))
                    
                except Exception as e:
                    date = round(time.time()*1000)
                    payload = {'clientId':clientId, 'clientSecret':clientSecret, 'date':date, 'username':new_user['username']}
                    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
                    requests.post('https://euapi.ttlock.com/v3/user/delete', headers=headers, params=payload)
                    selected_client.delete()
                    # print(e)
                    # return redirect('register')
                    # return HttpResponse(e)
                    return HttpResponse(status=400)

                # finally:
                #     return HttpResponse(status=400)


        except Exception as e:
            print(e)
            # return redirect('register')
            return HttpResponse(status=400)
                
        # return redirect('register')
        # finally:
        #     return HttpResponse(status=400)
            
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
@csrf_exempt
def loginUser(request):
    form = LoginForm()
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        email = data.get('email')
        password = data.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            # access_token = accessToken(request) # Done
            result = {}
            result["USER_TOKEN"] = user.access_token
            return HttpResponse(json.dumps(result), status=200)
        else:
            # return HttpResponse("{}, {}, {}".format(user, email, password))
            # print('email=', email,', password=',password)
            # print(user)
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


@csrf_exempt
def emailExists(request):
    data = json.loads(request.body.decode('utf-8'))
    email = data.get('email')

    try:
        User.objects.get(email=email)
        return HttpResponse(status=200)

    except User.DoesNotExist:
        return HttpResponse(status=400)

@csrf_exempt
def usernameExists(request):
    data = json.loads(request.body.decode('utf-8'))
    username = data.get('username')

    try:
        User.objects.get(username=username)
        return HttpResponse(status=200)

    except User.DoesNotExist:
        return HttpResponse(status=400)


@csrf_exempt
def is_email_exists(request):
    # data = json.loads(request.body.decode('utf-8'))
    # email = data.get('email')
    email = request

    try:
        User.objects.get(email=email)
        return True
    except User.DoesNotExist:
        return False

@csrf_exempt
def is_username_exists(request):
    # data = json.loads(request.body.decode('utf-8'))
    # username = data.get('username')
    username = request

    try:
        User.objects.get(username=username)
        return True
    except User.DoesNotExist:
        return False


@csrf_exempt
def passwordReset(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            email = data.get('email')
            print(email)
            if is_email_exists(email) == False:
                return HttpResponse(status=400)
            print(email)

            form = PasswordResetForm({'email': email})
            if form.is_valid():
                form.save(
                    request=request,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    # email_template_name='registration/password_reset_email.html',
                    # subject_template_name='registration/password_reset_subject.txt',
                )
                return HttpResponse(status=200)
                # return JsonResponse({'success': True, 'message': 'Password reset email has been sent.'})
            else:
                return HttpResponse(status=400)
                # return JsonResponse({'success': False, 'errors': form.errors})

        except Exception as e:
            return HttpResponse(status=400)

    else:
        return HttpResponse(status=400)
        # return JsonResponse({'success': False, 'message': 'Invalid request method.'})