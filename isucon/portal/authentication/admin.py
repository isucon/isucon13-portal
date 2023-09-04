from typing import Any
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from django.utils.translation import gettext_lazy as _
from django.contrib import admin
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from isucon.portal.authentication.models import User, Team, RegisterCoupon


admin.site.site_title = 'ISUCON Portal'
admin.site.site_header = 'ISUCON Portal'
admin.site.index_title = '管理'


class UserAdmin(DjangoUserAdmin):
    list_display = ["id", "username", "display_name", "team", "is_student", "is_staff"]
    list_filter = ["is_staff", "is_student", "team"]
    search_fields = ("username", "display_name", "email",)
    readonly_fields = ["username", "icon_tag"]

    fieldsets = (
        (None, {'fields': ('display_name', 'password', 'team', 'icon', 'icon_tag')}),
        (_('Personal info'), {'fields': ('username', 'email', 'is_student')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    def icon_tag(self, instance):
        # used in the admin site model as a "thumbnail"
        return mark_safe('<img src="{}" width="150" height="150" />'.format(instance.icon.thumbnail.url))
    icon_tag.short_description = 'Icon Preview'



admin.site.register(User, UserAdmin)


class TeamAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "owner", "is_active", "created_at", "declined_at"]
    list_filter = ["is_active"]
    search_fields = ["name"]

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return Team.original_manager.all()

admin.site.register(Team, TeamAdmin)


class RegisterCouponAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at", "used_at", "name", "team", "url")
    search_fields = ("name", )


    def url(self, obj):
        return "{}{}?token={}".format(settings.BASE_URL, reverse("create_team"), obj.token)

admin.site.register(RegisterCoupon, RegisterCouponAdmin)
