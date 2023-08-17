from django.utils.translation import gettext, gettext_lazy as _
from django.contrib import admin
from django.utils.safestring import mark_safe

from isucon.portal.authentication.models import User, Team

class UserAdmin(admin.ModelAdmin):
    list_display = ["id", "username", "display_name", "team", "is_student", "is_staff"]
    list_filter = ["is_staff", "is_student", "team"]
    search_fields = ("username", "display_name", "email",)
    readonly_fields = ["username", "icon_tag"]

    fieldsets = (
        (None, {'fields': ('display_name', 'password', 'team', 'icon', 'icon_tag')}),
        (_('Personal info'), {'fields': ('username', 'email',)}),
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
    list_display = ["id", "name", "owner", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["name"]

admin.site.register(Team, TeamAdmin)
