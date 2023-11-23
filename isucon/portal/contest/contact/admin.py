from typing import Any
from django.contrib import admin
from django.forms import BaseInlineFormSet
from django.http import HttpRequest
from isucon.portal.contest.contact import models

class TicketInlineFormset(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        initial = kwargs.get("initial", [])
        additional = [{"owner": self.request.user}]
        kwargs["initial"] = initial + additional
        super().__init__(*args, **kwargs)

class TicketCommentInline(admin.TabularInline):
    model = models.TicketComment
    extra = 1
    formset = TicketInlineFormset

    def get_formset(
        self, request: HttpRequest, obj: models.TicketComment | None = None, **kwargs: Any
    ) -> TicketInlineFormset:
        formset = super().get_formset(request, obj, **kwargs)
        formset.request = request
        return formset

class TicketAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'status', 'created_at', 'updated_at']
    list_filter = ['owner__team', 'status']
    search_fields = ['title', 'body']
    inlines = [TicketCommentInline]

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not obj:
          form.base_fields['owner'].initial = request.user
        return form

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['owner']
        else:
            return ['status']


admin.site.register(models.Ticket, TicketAdmin)
