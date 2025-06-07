from django.contrib import admin
from .models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Register custom user model with the admin site
# This allows the admin interface to manage users with the custom fields defined in the User model

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # custom user admin
    list_display = ('username', 'email', 'first_name',
                    'last_name', 'is_staff', 'created_at')
    # Filter options in the right sidebar of the list view
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'created_at')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    # Newest users first 
    ordering = ('-created_at',)

    # Fields to show in the user detail view
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('avatar', 'bio', 'created_at', 'updated_at')
        }),
    )

    # Fields to show in the add user form
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('first_name', 'last_name', 'email', 'avatar', 'bio')
        }),
    )

    # Timestamp fields are read only since they are automatically set
    readonly_fields = ('created_at', 'updated_at')