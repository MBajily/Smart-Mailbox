from django.db import models
from django.contrib.auth.models import User, Group, Permission, AbstractUser, BaseUserManager


class User(AbstractUser):
    class Role(models.TextChoices):
        CLIENT = "CLIENT", "Client"
        DELIVERY = "DELIVERY", "Delivery"

    base_role = Role.CLIENT

    username = None 
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

# ===============================================================
# =======================  Delivery  ============================
# ===============================================================
class DeliveryManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset(*args, **kwargs)
        return results.filter(role=User.Role.DELIVERY)


class Delivery(User):
    base_role = User.Role.DELIVERY

    delivery = DeliveryManager()

    class Meta:
        proxy = True

