from django.urls import path
from . import views

urlpatterns = [
	path('register/', views.register, name="register"),
	path('locks/list/', views.locksList, name="locksList"),
	path('passcode/random/', views.randomPasscode, name="randomPasscode"),
	path('lock/<str:lock_id>/details/', views.lockDetails, name="lockDetails"),
]