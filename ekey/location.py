import os
import datetime
import time
import json
from dotenv import load_dotenv
from api.models import Location
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt


load_dotenv()

clientId = os.getenv("CLIENT_ID")
clientSecret = os.getenv('CLIENT_SECRET')

# with open('/etc/config.json') as config_file:
#     config = json.load(config_file)

# clientId = config["CLIENT_ID"]
# clientSecret = config["CLIENT_SECRET"]


#https://maps.google.com/?q=<lat>,<lng>
@csrf_exempt
def lockLocation(request):
    if request.method == 'POST':
        auth_token = request.META.get('HTTP_USER_TOKEN')

        if auth_token is None:
            return HttpResponse(status=401)

        try:
            data = json.loads(request.body.decode('utf-8'))
            lock_id = data.get('lockId')
            latitude = data.get('latitude')
            longitude = data.get('longitude')

            date = round(time.time()*1000)
            payload = {'clientId':clientId, 'accessToken':auth_token, 'date':date, 'lockId':lock_id}
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            r = requests.get('https://cnapi.ttlock.com/v3/lock/detail', headers=headers, params=payload)
            
            if "errcode" in (r.json()):
                return HttpResponse(status=401)

            location = Location(lock_id=lock_id, latitude=latitude, longitude=longitude)
            location.save()

            return JsonResponse({"location":f"https://maps.google.com/?q={latitude},{longitude}"})

        except:
            return HttpResponse(status=401)

    return HttpResponse(status=401)


@csrf_exempt
def getLockLocation(request):
    if request.method == 'POST':
        auth_token = request.META.get('HTTP_USER_TOKEN')

        if auth_token is None:
            return HttpResponse(status=401)

        try:
            data = json.loads(request.body.decode('utf-8'))
            lock_id = data.get('lockId')

            location = Location.objects.filter(lock_id=lock_id).first()

            return JsonResponse({"location":f"https://maps.google.com/?q={location.latitude},{location.longitude}"})

        except:
            return HttpResponse(status=401)

    return HttpResponse(status=401)