from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    """Custom admin interface for the CustomUser model."""
    
    model = CustomUser
    list_display = ['email', 'first_name', 'last_name', 'date_of_birth', 'is_staff', 'is_active']
    list_filter = ['is_staff', 'is_active', 'date_joined']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {
            'fields': (
                'first_name', 
                'last_name', 
                'date_of_birth', 
                'profile_photo'
            )
        }),
        (_('Permissions'), {
            'fields': (
                'is_active', 
                'is_staff', 
                'is_superuser', 
                'groups', 
                'user_permissions'
            ),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 
                'first_name', 
                'last_name',
                'date_of_birth',
                'profile_photo',
                'password1', 
                'password2', 
                'is_staff', 
                'is_active'
            )}
        ),
    )
    
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['email']
    filter_horizontal = ('groups', 'user_permissions',)

# Register the custom user model with the admin site
admin.site.register(CustomUser, CustomUserAdmin)
