from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from . import models
from django.utils.translation import gettext as _


class UserAdmin(BaseUserAdmin):
    ordering = ["id"]
    list_display = ["full_name", "username", "phone_number", "email"]
    list_filter = ("is_admin",)
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal Info."), {"fields": ("phone_number", "email", "full_name")}),
        (_("Permissions"), {"fields": ("is_active", "is_superuser", "is_worker")}),
        (_("Important Dates"), {"fields": ("last_login",)}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "full_name",
                    "password1", "password2",
                ),
            },
        ),
    )


admin.site.register(models.CustomUser, UserAdmin)
