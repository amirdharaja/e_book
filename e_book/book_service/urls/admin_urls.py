from django.urls import path

from book_service.controllers.admin_controller import (
    get_book,
    list_all_books,
    add_new_book,
    delete_author_books,
    delete_all_books
)

urlpatterns = [
    path('book', get_book),
    path('books', list_all_books),
    path('new', add_new_book),
    path('delete/author-books', delete_author_books),
    path('delete/all-books', delete_all_books),
]