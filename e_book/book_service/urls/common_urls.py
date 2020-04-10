from django.urls import path

from book_service.controllers.common_controller import (
    login,
    register,
    get_profile,
    update_profile,
    delete_account,
    reset_password,
    logout
)

urlpatterns = [
    path('login', login),
    path('register', register),
    path('profile', get_profile),
    path('update', update_profile),
    path('profle/delete', delete_account),
    path('password/reset', reset_password),
    path('logout', logout),
]