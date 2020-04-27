from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Permission
from django.urls import reverse, re_path, path
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import mark_safe
import nested_admin

from coreapp import models as m


admin.site.site_header = "RAD Django DRF SK Admin"
admin.site.site_title = "RAD Django DRF SK Admin"
admin.site.index_title = "Welcome to RAD Django DRF SK Admin"


class DBViewAdmin(admin.ModelAdmin):
    list_display_links = None
    actions = None

    def has_add_permission(self, request):  # hide Add button
        return False


@admin.register(m.User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("full_name",)}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "password1", "password2"),}),
    )
    list_display = ("email", "roles_and_groups", "is_staff", "is_superuser")
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    search_fields = ("full_name", "email")
    ordering = ("email",)
    filter_horizontal = (
        "groups",
        "user_permissions",
    )

    def roles_and_groups(self, obj):
        return ", ".join([g.name for g in obj.groups.all()])


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    model = Permission
    list_display = (
        "desc",
        "codename",
    )

    def desc(self, obj):
        return str(obj)
