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


class IsSetListFilter(admin.SimpleListFilter):
    title = "フィールド"
    parameter_name = "fieldname_is_set"
    field = "fieldname"

    def lookups(self, request, model_admin):
        return [
            ("true", "はい"),
            ("false", "いいえ"),
        ]

    def queryset(self, request, queryset):
        if self.value() == "true":
            return queryset.filter(**{
                self.field + "__isnull": False
            })
        if self.value() == "false":
            return queryset.filter(**{
                self.field + "__isnull": True
            })


class DiscordListFilter(IsSetListFilter):
    title = "Discord連携"
    parameter_name = "discord_is_connected"
    field = "discord_expired_at"


class ParticipateListFilter(IsSetListFilter):
    title = "参加"
    parameter_name = "participate"
    field = "team"


class UserAdmin(DjangoUserAdmin):
    list_display = ["id", "username", "display_name", "team", "discord_username", "discord_expired_at", "is_student", "is_staff"]
    list_filter = [
        DiscordListFilter, ParticipateListFilter,
        "is_staff", "is_student",
        "team",
    ]
    search_fields = ("username", "display_name", "email",)
    readonly_fields = ["username", "icon_tag"]

    fieldsets = (
        (None, {'fields': ('display_name', 'password', 'team', 'icon', 'icon_tag')}),
        (_('Personal info'), {'fields': ('username', 'email', 'is_student')}),
        ('Discord', {'fields': ('discord_id', 'discord_username', 'discord_expired_at')}),
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


class EnvCheckListFilter(IsSetListFilter):
    title = "環境チェック"
    parameter_name = "envcheck_was_done"
    field = "envchecked_at"


class TeamAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "owner", "is_guest", "is_active", "envcheck_was_done", "created_at", "declined_at"]
    list_filter = ["is_active", "is_guest", "want_local_participation", "is_local_participation", EnvCheckListFilter]
    search_fields = ["name"]

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return Team.original_manager.all()

    def envcheck_was_done(self, obj):
        return obj.envchecked_at != None
    envcheck_was_done.boolean = True
    envcheck_was_done.admin_order_field = "envchecked_at"
    envcheck_was_done.short_description = "環境"

admin.site.register(Team, TeamAdmin)


class RegisterCouponAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at", "used_at", "name", "team", "url")
    search_fields = ("name", )


    def url(self, obj):
        return "{}{}?token={}".format(settings.BASE_URL, reverse("create_team"), obj.token)

admin.site.register(RegisterCoupon, RegisterCouponAdmin)
