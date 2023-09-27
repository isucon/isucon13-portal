from django.contrib import admin

from isucon.portal.envcheck.models import EnvCheckResult


class EnvCheckResultAdmin(admin.ModelAdmin):
    list_display = ["id", "created_at", "name", "passed", "team"]
    list_filter = ["team", "passed", "name"]


admin.site.register(EnvCheckResult, EnvCheckResultAdmin)
