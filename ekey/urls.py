from django.urls import path
from . import views

urlpatterns = [
	path('register/', views.register, name="register"),
	path('locks/list/', views.locksList, name="locksList"),
]