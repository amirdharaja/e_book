from django.db import models
from book_service.models import Login


class Book(models.Model):

    title         =    models.CharField(max_length=255, null=False)
    amazon_url    =    models.CharField(max_length=255, null=True)
    author        =    models.ForeignKey(Login, on_delete=models.CASCADE, unique=False)
    genre         =    models.CharField(max_length=32, null=False)
    created_at    =    models.DateTimeField(auto_now_add=True)
    updated_at    =    models.DateTimeField(null=True)

    objects = models.Manager()

    class Meta:
        db_table = "books"