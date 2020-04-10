from django.urls import path

from book_service.controllers.author_controller import (
    get_my_book,
    list_my_books,
    add_new_book,
    delete_my_book,
    delete_my_books
)

urlpatterns = [
    path('book', get_my_book),
    path('books', list_my_books),
    path('new', add_new_book),
    path('delete', delete_my_book),
    path('delete/all-books', delete_my_books),
]