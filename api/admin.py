from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import (
    Availability,
    Booking,
    ChildProfile,
    LSAProfile,
    Profile,
    Review,
    Specialization,
    User,
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ["email", "first_name", "last_name", "role", "is_active", "created_at"]
    list_filter = ["role", "is_active", "is_email_verified"]
    search_fields = ["email", "first_name", "last_name"]
    ordering = ["-created_at"]
    fieldsets = BaseUserAdmin.fieldsets + (
        ("HabotConnect", {"fields": ("role", "is_email_verified")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "first_name", "last_name", "role", "password1", "password2"),
            },
        ),
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "city", "country", "phone_number"]
    search_fields = ["user__email", "user__first_name", "user__last_name", "city"]


@admin.register(LSAProfile)
class LSAProfileAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "headline",
        "hourly_rate",
        "average_rating",
        "review_count",
        "is_verified",
        "is_available",
    ]
    list_filter = ["is_verified", "is_available", "crb_dbs_checked", "first_aid_trained"]
    search_fields = ["user__email", "user__first_name", "user__last_name", "headline"]
    filter_horizontal = ["specializations"]


@admin.register(Specialization)
class SpecializationAdmin(admin.ModelAdmin):
    search_fields = ["name"]


@admin.register(ChildProfile)
class ChildProfileAdmin(admin.ModelAdmin):
    list_display = ["__str__", "parent", "date_of_birth", "school_name"]
    search_fields = ["first_name", "last_name", "parent__email"]


@admin.register(Availability)
class AvailabilityAdmin(admin.ModelAdmin):
    list_display = ["lsa", "day_of_week", "specific_date", "start_time", "end_time", "is_booked"]
    list_filter = ["day_of_week", "is_recurring", "is_booked"]


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ["id", "parent", "lsa", "status", "starts_at", "total_hours"]
    list_filter = ["status", "starts_at"]
    search_fields = ["parent__email", "lsa__email"]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["booking", "rating", "would_recommend", "created_at"]
    list_filter = ["rating", "would_recommend"]
