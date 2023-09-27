import functools

from django.contrib.auth.decorators import user_passes_test
from django.conf import settings
from django.shortcuts import redirect
from django.utils import timezone
from django.http import HttpResponse

from isucon.portal.authentication.models import Team

def has_team(user):
    return user.is_authenticated and user.team is not None

team_is_authenticated = user_passes_test(has_team)

def is_registration_available():
    """登録可能か日時チェック"""
    now = timezone.now()
    return settings.REGISTRATION_START_AT <= now <= settings.REGISTRATION_END_AT

def is_team_modify_available():
    """チーム情報変更可能か日時チェック"""
    now = timezone.now()
    return now <= settings.TEAM_MODIFY_END_AT

def check_registration(function):
    @functools.wraps(function)
    def _function(request, *args, **kwargs):
        if not is_registration_available():
            return redirect("index")
        return function(request, *args, **kwargs)
    return _function

def envcheck_token_required(function):
    """チームトークンによる認証"""
    @functools.wraps(function)
    def _function(request, *args, **kwargs):
        authorization_header = request.headers.get("Authorization")
        try:
            if not authorization_header:
                raise ValueError()
            method, token = authorization_header.split(" ", 1)
            if method.lower() != "bearer":
                raise ValueError()
            team = Team.objects.get(envcheck_token=token)
        except (ValueError, Team.DoesNotExist):
            return HttpResponse(status=401)

        request.team = team
        return function(request, *args, **kwargs)
    return _function
