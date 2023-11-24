from typing import Any
from django.contrib import admin
from django.forms import BaseInlineFormSet
from django.http import HttpRequest
from isucon.portal.contest.contact import models
from django.urls import reverse
from django.utils.safestring import mark_safe 

class TicketInlineFormset(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        initial = kwargs.get("initial", [])
        additional = [{"owner": self.request.user}]
        kwargs["initial"] = initial + additional
        super().__init__(*args, **kwargs)

class TicketCommentInline(admin.StackedInline):
    model = models.TicketComment
    extra = 1
    formset = TicketInlineFormset
    readonly_fields = ['created_at', 'is_staff']
    ordering = ['created_at']

    def get_formset(
        self, request: HttpRequest, obj: models.TicketComment | None = None, **kwargs: Any
    ) -> TicketInlineFormset:
        formset = super().get_formset(request, obj, **kwargs)
        formset.request = request
        return formset
    
    def is_staff(self, obj):
        if obj.owner.is_staff:
            return 'スタッフ'
        else:
            return '参加者'
    is_staff.short_description = 'staff'

class TicketAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'status', 'created_at', 'updated_at']
    list_filter = ['status', 'owner__team']
    search_fields = ['title', 'body']
    inlines = [TicketCommentInline]

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not obj:
          form.base_fields['owner'].initial = request.user
        return form

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['team_link', 'owner', 'created_at', 'updated_at']
        else:
            return ['status']
    
    def team_link(self, obj):
        return mark_safe(
            '<a href="{}">{}</a> ('.format(
                reverse('admin:authentication_team_change', args=(obj.owner.team.id,)),
                obj.owner.team.name
            ) + 
            ' / '.join([
                '<a href="{}?{}">サーバ一覧</a>'.format(
                    reverse('admin:contest_server_changelist'),
                    'team__id__exact={}'.format(obj.owner.team.id),
                ),
                '<a href="{}?{}">ジョブ一覧</a>'.format(
                    reverse('admin:contest_job_changelist'),
                    'team__id__exact={}'.format(obj.owner.team.id),
                ),
                '<a href="{}?{}">チームスコア</a>'.format(
                    reverse('admin:contest_score_changelist'),
                    'team__id__exact={}'.format(obj.owner.team.id),
                ),
            ]) +
            ')'
        )
    team_link.short_description = 'team'

admin.site.register(models.Ticket, TicketAdmin)
