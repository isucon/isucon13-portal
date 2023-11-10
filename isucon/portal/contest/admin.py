from django.contrib import admin
from django import forms

from isucon.portal.contest.models import (
    Server,
    Information,
    Score,
    Job
)


class ServerAdmin(admin.ModelAdmin):
    list_display = ["id", "hostname", "global_ip", "private_ip"]
    list_filter = ["hostname"]

admin.site.register(Server, ServerAdmin)


class InformationAdminForm(forms.ModelForm):
    class Meta:
        model = Information
        fields = ["id", "is_enabled", "title", "description"]



class InformationAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "is_enabled"]
    list_filter = ["is_enabled"]
    form = InformationAdminForm

admin.site.register(Information, InformationAdmin)


class ScoreAdmin(admin.ModelAdmin):
    list_display = ["id", "team", "best_score", "latest_score", "latest_is_passed"]
    list_filter = ["latest_is_passed"]

admin.site.register(Score, ScoreAdmin)

class JobAdmin(admin.ModelAdmin):
    list_display = ["id", "team", "status", "target", "is_passed", "score", "reason_short"]
    list_filter = ["status", "is_passed", "team"]

    def reason_short(self, instance):
        line = instance.reason.split("\n")[0]
        return line
    reason_short.short_description = "結果 (抜粋)"


admin.site.register(Job, JobAdmin)
