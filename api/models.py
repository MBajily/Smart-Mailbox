from django.db import models
from django.contrib.auth.models import User, Group, Permission, AbstractUser, BaseUserManager
from django.dispatch import receiver
from django.db.models.signals import post_save


class User(AbstractUser):
    class Role(models.TextChoices):
        USER = "USER", "User"
        DELIVERY = "DELIVERY", "Delivery"

    base_role = Role.USER

    last_login = None 
    first_name = None 
    last_name = None 
    is_staff = None 
    is_superuser = None 
    groups_id = None 
    user_permissions_id = None 
    user_permissions = None
    groups = None
    email = models.EmailField(unique=True)
    is_deleted = models.BooleanField(null=False, default=False)
    access_token = models.CharField(max_length=50, null=True)
    hashed_password = models.CharField(max_length=100, null=True)
    username = models.CharField(max_length=50, unique=True, null=True) 
    ttlock_username = models.CharField(max_length=100, unique=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    role = models.CharField(max_length=50, choices=Role.choices)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.role = self.base_role
            return super().save(*args, **kwargs)


# ===============================================================
# =====================  User Profile  ==========================
# ===============================================================
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created and instance.role == 'USER':
        UserProfile.objects.create(user=instance)

class UserProfile(models.Model):
    Gender = (
        (1, 'Male'),
        (2, 'Female'),
        (3, 'Prefer not to say')
        )
    user = models.OneToOneField(User, on_delete=models.CASCADE, name="user")
    full_name = models.CharField(max_length= 100, null=True)
    phone = models.CharField(max_length=30, null=True)
    birth_date = models.DateField(null=True)
    gender = models.IntegerField(choices=Gender, null=True)


# ===============================================================
# =========================  Lock  ==============================
# ===============================================================
class Lock(models.Model):
    lock_id = models.IntegerField(primary_key=True, editable=False)
    name = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now_add=True)


class Lock_Owner(models.Model):
    lock = models.ForeignKey(Lock, null=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    date = models.DateTimeField(auto_now_add=True)
    

# ===============================================================
# ========================  Group  ==============================
# ===============================================================
class Group(models.Model):
    group_id = models.IntegerField(primary_key=True, editable=False)
    name = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now_add=True)


class Lock_Group(models.Model):
    lock = models.ForeignKey(Lock, null=True, on_delete=models.SET_NULL)
    group = models.ForeignKey(Group, null=True, on_delete=models.SET_NULL)
    date = models.DateTimeField(auto_now_add=True)


# ===============================================================
# =========================  Ekey  ==============================
# ===============================================================
class Ekey(models.Model):
    ekey_id = models.IntegerField(primary_key=True, editable=False)
    lock = models.ForeignKey(Lock, null=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=100)
    remarks = models.TextField(null=True)
    start_date = models.DateTimeField(auto_now_add=True, null=True)
    end_date = models.DateTimeField(null=True)
    date = models.DateTimeField(auto_now_add=True)


# ===============================================================
# =======================  Passcode  ============================
# ===============================================================
class Passcode(models.Model):
    PasscodeTypes = (
        ('One-time','One-time'), 
        ('Permanent', 'Permanent'),
        ('Timed', 'Timed'),
        ('Custom', 'Custom'),
        ('Recurring', 'Recurring'),
        ('Erase', 'Erase'),
        )
    passcode_id = models.IntegerField(primary_key=True, editable=False)
    lock = models.ForeignKey(Lock, null=True, on_delete=models.SET_NULL)
    passcode = models.IntegerField()
    name = models.CharField(max_length=100, null=True)
    type = models.CharField(max_length=50, choices=PasscodeTypes)
    start_date = models.DateTimeField(auto_now_add=True, null=True)
    end_date = models.DateTimeField(null=True)
    date = models.DateTimeField(auto_now_add=True)


# ===============================================================
# =======================  Message  =============================
# ===============================================================
class Notification(models.Model):
    notification_id = models.IntegerField(primary_key=True, editable=False)
    receiver = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    subject = models.CharField(max_length=50)
    message = models.CharField(max_length=500)
    date = models.DateTimeField(auto_now_add=True)


# ===============================================================
# ====================  Notifications  ==========================
# ===============================================================
class Record(models.Model):
    record_id = models.IntegerField(primary_key=True, editable=False)
    lockId = models.CharField(max_length=100, null=True)
    recordType = models.CharField(max_length=100, null=True)
    success = models.CharField(max_length=100, null=True)
    keyboardPwd = models.CharField(max_length=100, null=True)
    lockDate = models.DateTimeField(auto_now_add=True, null=True)


# ===============================================================
# =======================  Alarm  ===============================
# ===============================================================
class Alarm(models.Model):
    AlarmTypes = (
        ('Lock', 0),
        ('Unlock', 1),
        ('Warning', 2)
        )
    alarm_id = models.IntegerField(primary_key=True, editable=False)
    lock = models.ForeignKey(Lock, null=True, on_delete=models.SET_NULL)
    receiver = models.CharField(max_length=100)
    type = models.CharField(max_length=50, choices=AlarmTypes)
    date = models.DateTimeField(auto_now_add=True)



# ===============================================================
# =====================  Location  ==============================
# ===============================================================
class Location(models.Model):
    lock_id = models.IntegerField(primary_key=True, null=False)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)

    def __str__(self):
        return f"https://maps.google.com/?q={self.latitude},{self.longitude}"