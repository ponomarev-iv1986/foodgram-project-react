from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        'email',
        'username',
        'first_name',
        'last_name',
        'is_staff',
        'is_superuser',
        'is_active'
    ]
    list_filter = ['email', 'username']
