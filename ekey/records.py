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


load_dotenv()

clientId = os.getenv("CLIENT_ID")
clientSecret = os.getenv('CLIENT_SECRET')

# with open('/etc/config.json') as config_file:
#     config = json.load(config_file)

# clientId = config["CLIENT_ID"]
# clientSecret = config["CLIENT_SECRET"]

ttlock = TTLock(clientId, clientSecret)


@csrf_exempt
def recordsCallback(request):
	if request.method == "POST":
		data = json.loads(request.body.decode('utf-8'))
		lockId = data.get('lockId')
		data = json.loads(data.get('records'))
		recordType = data.get('recordType')
		success = data.get('success')
		keyboardPwd = data.get('keyboardPwd')
		lockDate = datetime.fromtimestamp(data.get('lockDate'))

		response = {"success"} 
		return HttpResponse(json.dumps(response), status=200)