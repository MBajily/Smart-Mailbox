from django.db import models
from django.contrib.auth.models import User, Group, Permission, AbstractUser, BaseUserManager
from django.dispatch import receiver
from django.db.models.signals import post_save


class User(AbstractUser):
    class Role(models.TextChoices):
        USER = "USER", "User"
        DELIVERY = "DELIVERY", "Delivery"

    base_role = Role.USER

    username = models.CharField(max_length=50, unique=True, null=True) 
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
    Sex = (
        ('Male', 'Male'),
        ('Female', 'Female')
        )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=30)
    birth_date = models.DateField(auto_now_add=True)
    sex = models.CharField(max_length=50, choices=Sex)


# ===============================================================
# =========================  Lock  ==============================
# ===============================================================
class Lock(models.Model):
    lock_id = models.IntegerField(primary_key=True, editable=False)
    name = models.CharField(max_length=100)
    # location = 
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
    passcode = models.TextField(max_length=15)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=50, choices=PasscodeTypes)
    start_date = models.DateTimeField(auto_now_add=True, null=True)
    end_date = models.DateTimeField(null=True)
    date = models.DateTimeField(auto_now_add=True)


# ===============================================================
# ========================  Record  =============================
# ===============================================================
class Record(models.Model):
    Stauts = (
        ('Lock', 0),
        ('Unlock', 1),
        ('Failed', 2)
        )
    Methods = (
        ('App', 'App'),
        ('Pin', 'Pin'),
        )

    record_id = models.IntegerField(primary_key=True, editable=False)
    lock = models.ForeignKey(Lock, null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=50, choices=Stauts)
    method = models.CharField(max_length=50, choices=Methods)
    date = models.DateTimeField(auto_now_add=True)


# ===============================================================
# ====================  Notifications  ==========================
# ===============================================================
class Notification(models.Model):
    notification_id = models.IntegerField(primary_key=True, editable=False)
    sender = models.CharField(max_length=100)
    receiver = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    content = models.CharField(max_length=1000)
    date = models.DateTimeField(auto_now_add=True)


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
