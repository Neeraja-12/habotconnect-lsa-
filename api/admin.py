from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Profile, LSAProfile, Specialization, ChildProfile, Booking, Availability, Review

# Register User with custom admin
class CustomUserAdmin(UserAdmin):
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role'),
        }),
    )
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Custom fields', {'fields': ('role', 'is_email_verified')}),
    )
    
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)

admin.site.register(User, CustomUserAdmin)

# ✅ Register all other models
admin.site.register(Profile)
admin.site.register(LSAProfile)
admin.site.register(Specialization)
admin.site.register(ChildProfile)
admin.site.register(Booking)
admin.site.register(Availability)
admin.site.register(Review)