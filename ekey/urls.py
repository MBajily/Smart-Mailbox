from django.urls import path
from . import views, passcode, lock, profile, records, location, notifications
from django.views.decorators.csrf import csrf_exempt


urlpatterns = [
    # User
    path('register/', views.register, name="register"),
    path('email/check/', views.emailExists, name="email_exists"),
    path('username/check/', views.usernameExists, name="username_exists"),
    path('login/', views.loginUser, name="login"),
    path('logout/', views.logoutUser, name="logout"),

    # User Profile
    path('profile/', profile.profile, name="profile"),
    path('profile/update/', profile.profileUpdate, name="profileUpdate"),

    # Lock
    path('lock/init/', lock.lockInit, name="lockInit"),
    path('lock/list/', lock.lockList, name="lockList"),
    path('lock/details/', lock.lockDetails, name="lockDetails"),
    path('lock/name/update/', lock.lockNameUpdate, name="lockNameUpdate"),
    path('lock/sound/update/', lock.lockSoundUpdate, name="lockSoundUpdate"),
    path('lock/delete/', lock.lockDelete, name="lockDelete"),

    # Lock Location
    path('lock/location/', location.lockLocation, name="lockLocation"),
    path('lock/location/get/', location.getLockLocation, name="getLockLocation"),

    # Passcode
    path('lock/passcode/list/', passcode.passcodeList, name="passcodeList"),
    path('lock/passcode/new/', passcode.passcodeNew, name="passcodeNew"),
    path('lock/passcode/update/', passcode.passcodeUpdate, name="passcodeUpdate"),
    path('lock/passcode/delete/', passcode.passcodeDelete, name="passcodeDelete"),

    # Records
    path('records/callback/', records.recordsCallback, name="recordsCallback"),
    path('records/', records.records, name="records"),

    # Reset Password
    path('password/reset/', views.passwordReset, name="password_reset"),

    # Notifications
    path('notifications/', notifications.notifications, name="notifications"),
    ]