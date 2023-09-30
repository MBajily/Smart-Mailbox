from django.urls import path
from . import views, passcode

urlpatterns = [
	path('register/', views.register, name="register"),
	path('login/', views.loginUser, name="login"),
	path('logout/', views.logoutUser, name="logout"),
	path('lock/list/', views.listLock, name="listLock"),
	path('lock/<str:lock_id>/details/', views.lockDetails, name="lockDetails"),
	path('<str:lock_id>/passcode/<str:type_id>/new/', passcode.getPasscode, name="getPasscode"),
	path('<str:lock_id>/passcode/<str:passcode_id>/delete/', passcode.deletePasscode, name="deletePasscode"),
	path('<str:lock_id>/passcode/list/', passcode.listPasscode, name="listPasscode"),
	path('<str:lock_id>/passcode/<str:passcode_id>/update/<str:passcode>/', passcode.updatePasscode, name="updatePasscode"),
]