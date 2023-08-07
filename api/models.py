from django.db import models
from django.contrib.auth.models import User, Group, Permission, AbstractUser, BaseUserManager


class User(AbstractUser):
    class Role(models.TextChoices):
        CLIENT = "CLIENT", "Client"
        DELIVERY = "DELIVERY", "Delivery"

    base_role = Role.CLIENT

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
# ========================  Client  =============================
# ===============================================================
class ClientManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset(*args, **kwargs)
        return results.filter(role=User.Role.CLIENT)


class Client(User):
    base_role = User.Role.CLIENT

    client = ClientManager()

    class Meta:
        proxy = True


class Lock(models.Model):
    # user = 
    lock_id = models.CharField(primary_key=True, max_length=20, unique=True)
    lock_name = models.CharField(max_length=100)
    lock_alias = models.CharField(max_length=100)
    lock_mac = models.CharField(max_length=100)
    # group = 
    key_id = models.CharField(max_length=20, unique=True)
    date = models.DateField(auto_now_add=True,)
    