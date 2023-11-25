from django.contrib import admin
from django import forms

from isucon.portal.contest.models import (
    Server,
    Information,
    Score,
    Job
)


class ServerAdmin(admin.ModelAdmin):
    list_display = ["id", "team", "global_ip", "private_ip", "is_checked", "is_bench_target"]
    list_filter = ["team", "is_checked"]

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
    list_display = [
        "id", "team", "best_score", "latest_score", "latest_is_passed",
        "test_score", "test_is_passed", "language",
    ]
    list_filter = ["latest_is_passed", "test_is_passed", "language"]

admin.site.register(Score, ScoreAdmin)


class JobAdmin(admin.ModelAdmin):
    list_display = [
        "id", "team", "status", "created_at", "updated_at", "is_active", "is_test", "is_passed",
        "score", "resolved_count", "language", "reason_short"
    ]
    list_filter = ["status", "is_passed", "is_test", "is_active", "language", "team"]

    def reason_short(self, instance):
        line = instance.reason.split("\n")[0]
        return line
    reason_short.short_description = "結果 (抜粋)"


admin.site.register(Job, JobAdmin)
