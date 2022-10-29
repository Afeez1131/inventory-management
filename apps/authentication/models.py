from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, **other_fields):
        user = self.model(username=username, **other_fields)
        user.set_password(password)

        user.is_worker = True
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **other_fields):
        user = self.create_user(username=username, password=password, **other_fields)
        user.is_superuser = True
        user.is_admin = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    full_name = models.CharField(max_length=255)
    username = models.CharField(max_length=155, unique=True)
    phone_number = models.CharField(max_length=11)
    email = models.EmailField()

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_worker = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["phone_number", "full_name"]

    def __str__(self):
        return self.full_name

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin
