from django.db import models
from datetime import datetime

from book_service.models import Login

class LoginHistory(models.Model):

    login        =   models.ForeignKey(Login, on_delete=models.CASCADE, unique=False)
    login_at     =   models.DateTimeField()

    objects = models.Manager()


    class Meta:
        db_table = "login_history"