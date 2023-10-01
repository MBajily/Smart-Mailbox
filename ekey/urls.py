from django.urls import path
from . import views, passcode

urlpatterns = [
	path('register/', views.register, name="register"),
	path('login/', views.loginUser, name="login"),
	path('logout/', views.logoutUser, name="logout"),
	path('lock/list/', views.lockList, name="lockList"),
	path('lock/<str:lock_id>/details/', views.lockDetails, name="lockDetails"),
	path('lock/<str:lock_id>/delete/', views.lockDelete, name="lockDelete"),
	path('lock/<str:lock_id>/passcode/<str:type_id>/new/', passcode.passcodeNew, name="passcodeNew"),
	path('lock/<str:lock_id>/passcode/<str:passcode_id>/delete/', passcode.passcodeDelete, name="passcodeDelete"),
	path('lock/<str:lock_id>/passcode/list/', passcode.passcodeList, name="passcodeList"),
	path('lock/<str:lock_id>/passcode/<str:passcode_id>/update/<str:passcode>/', passcode.passcodeUpdate, name="passcodeUpdate"),
]