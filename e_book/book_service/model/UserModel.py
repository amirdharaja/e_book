from django.db import models

from book_service.models import Login


class User(models.Model):

    login               =    models.ForeignKey(Login, on_delete=models.CASCADE, unique=False)
    first_name          =    models.CharField(max_length=255, null=False)
    last_name           =    models.CharField(max_length=255, null=True)
    gender              =    models.CharField(max_length=16, null=False)
    phone_number        =    models.CharField(max_length=32, null=False)
    email               =    models.CharField(max_length=255, null=False)
    permanent_address   =    models.CharField(max_length=255, null=True)
    temporary_address   =    models.CharField(max_length=255, null=False)
    pincode             =    models.CharField(max_length=16, null=False)
    created_at          =    models.DateTimeField(auto_now_add=True)
    updated_at          =    models.DateTimeField(null=True)

    objects = models.Manager()

    class Meta:
        db_table = "users"