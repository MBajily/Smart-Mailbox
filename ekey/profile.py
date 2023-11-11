import os
import requests
import datetime
import time
import json
from django.shortcuts import render, redirect
from ttlockwrapper import TTLock
from dotenv import load_dotenv
from api.models import *
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


@csrf_exempt
def profile(request):
    try:
        auth_token = request.META.get('HTTP_USER_TOKEN')
        if auth_token is None:
            return HttpResponse(status=401)

        result = {}
        selectedUser = User.objects.get(access_token=auth_token)
        profile = UserProfile.objects.get(user=selectedUser)
        result["full_name"] = profile.full_name
        result["phone"] = profile.phone
        result["gender"] = profile.gender
        result["birth_date"] = {}
        result["birth_date"]["year"] = profile.birth_date.year
        result["birth_date"]["month"] = profile.birth_date.month
        result["birth_date"]["day"] = profile.birth_date.day
        return HttpResponse(json.dumps(result), status=200)

    except Exception as e:
        return HttpResponse(status=401)


@csrf_exempt
def profileUpdate(request):
    if request.method == "POST":
        try:
            auth_token = request.META.get('HTTP_USER_TOKEN')
            if auth_token is None:
                return HttpResponse(status=401)

            data = json.loads(request.body.decode('utf-8'))
            selectedUser = User.objects.get(access_token=auth_token)
            profile = UserProfile.objects.get(user=selectedUser)

            profile.full_name = data.get("full_name")
            profile.phone = data.get("phone")
            profile.gender = data.get("gender")
            profile.birth_date = data.get("birth_date")

            profile.save()
            result = {}
            result["full_name"] = profile.full_name
            result["phone"] = profile.phone
            result["gender"] = profile.gender
            result["birth_date"] = {}
            result["birth_date"] = profile.birth_date

            return HttpResponse(json.dumps(result), status=200)

        except Exception as e:
            return HttpResponse(e)
