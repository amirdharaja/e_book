from django.contrib import admin
from book_service.models import Login
from book_service.model.UserModel import User


class LoginAdmin(admin.ModelAdmin):
    list_display = ['username', 'role', 'active']
    search_fields = ['username']

class UserAdmin(admin.ModelAdmin):
    list_display = ['login_id',]
    search_fields = ['login_id']

admin.site.register(User, UserAdmin)
