from django.db import models

from book_service.models import Login
from book_service.model.BookModel import Book


class UserBook(models.Model):

    login         =    models.ForeignKey(Login, on_delete=models.CASCADE, unique=False)
    book          =    models.ForeignKey(Book, on_delete=models.CASCADE, unique=False)
    created_at    =    models.DateTimeField(auto_now_add=True)
    updated_at    =    models.DateTimeField(null=True)

    objects = models.Manager()

    class Meta:
        db_table = "user_books"