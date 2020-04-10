from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, username, password=None, role=None, is_active=True, is_admin=False, is_staff=False):
        if not username:
            raise ValueError('Email required')
        if not password:
            raise ValueError('Password required')
        user_obj = self.model(
            username = self.normalize_email(username)
        )
        user_obj.set_password(password)
        user_obj.role = role
        user_obj.active = is_active
        user_obj.is_superuser = is_admin
        user_obj.is_staff= is_staff
        user_obj.save(using=self._db)
        return user_obj

    def create_staffuser(self, username, password):
        user = self.create_user(
            username,
            password=password,
            role='super_admin',
            is_staff=True
        )
        return user

    def create_superuser(self, username, password):
        user = self.create_user(
            username,
            password=password,
            role='super_admin',
            is_staff=True
        )
        return user

class Login(AbstractBaseUser):

    username        =    models.CharField(max_length=255, null=False, unique=True)
    password        =    models.CharField(max_length=255, null=False)
    role            =    models.CharField(default='faculty', null=False, max_length=32)
    active          =    models.BooleanField(default=True)
    last_login      =    models.DateTimeField(null=True)
    created_at      =    models.DateTimeField(auto_now_add=True)
    updated_at      =    models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username
    
    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_active(self):
        return self.active

    class Meta:
        db_table = "login"
