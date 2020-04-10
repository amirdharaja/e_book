from django.db import models
from book_service.models import Login

class Token(models.Model):

    login       =    models.ForeignKey(Login, on_delete=models.CASCADE, unique=True)
    token       =    models.CharField(max_length=512, null=False)
    created_at  =    models.DateTimeField(auto_now_add=True)
    updated_at  =    models.DateTimeField(null=True)

    objects = models.Manager()

    class Meta:
        db_table = "tokens"