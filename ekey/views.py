import os
import hashlib
from django.shortcuts import render, redirect
from ttlockwrapper import TTLock
import pprint
from dotenv import load_dotenv

load_dotenv()

clientId = os.getenv("CLIENT_ID")
clientSecret = os.getenv('CLIENT_SECRET')

ttlock = TTLock(clientId, clientSecret)

# Create your views here.
def register(request):
	if request.method == 'POST':
		email = request.POST['email']
		password = request.POST['password']
		if password == request.POST['confirm']:
			username = str(email.split('@')[0])
			print(username)
			password = (hashlib.md5(password.encode()).hexdigest())
		
			ttlock.create_user(clientId=clientId, clientSecret=clientSecret, username=username, password=password)

	context = {'title':'Register'}
	
	return render(request, 'ekey/register.html', context)
