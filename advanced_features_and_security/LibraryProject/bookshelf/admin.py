from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, Book

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['email', 'first_name', 'last_name', 'date_of_birth', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        (_('Additional Info'), {'fields': ('date_of_birth', 'profile_photo')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (_('Additional Info'), {'fields': ('date_of_birth', 'profile_photo')}),
    )

class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'created_by', 'created_at']
    list_filter = ['created_at', 'author']
    search_fields = ['title', 'author', 'isbn']

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Book, BookAdmin)
