from django.urls import path

from book_service.controllers.user_controller import (
    get_book,
    list_all_books,
    add_favourite_book,
    remove_favourite_book,
    remove_all_favourite_books,
    list_all_favourite_books,
    add_cart,
    remove_cart,
    remove_all_carts,
    list_all_carts
)

urlpatterns = [
    path('book', get_book),
    path('books', list_all_books),
    path('favourite/add', add_favourite_book),
    path('favourite/remove', remove_favourite_book),
    path('favourite/remove/all', remove_all_favourite_books),
    path('favourite/books', list_all_favourite_books),
    path('cart/add', add_cart),
    path('cart/remove', remove_cart),
    path('cart/remove/all', remove_all_carts),
    path('cart/books', list_all_carts),
]