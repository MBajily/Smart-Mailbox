from django.urls import path
from . import views

urlpatterns = [
	path('register/', views.register, name="register"),
	path('lock/list/', views.listLock, name="listLock"),
	path('lock/<str:lock_id>/details/', views.lockDetails, name="lockDetails"),
	path('<str:lock_id>/passcode/<str:type_id>/new/', views.getPasscode, name="getPasscode"),
	path('<str:lock_id>/passcode/<str:passcode_id>/delete/', views.deletePasscode, name="deletePasscode"),
	path('<str:lock_id>/passcode/list/', views.listPasscode, name="listPasscode"),
	
]