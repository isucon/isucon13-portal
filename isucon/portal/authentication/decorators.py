import functools

from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.shortcuts import redirect
from django.utils import timezone
from django.http import HttpResponse

from isucon.portal.authentication.models import Team


def team_is_authenticated(function):
    @functools.wraps(function)
    def _function(request, *args, **kwargs):
        user = request.user
        if user.team is None:
            return redirect("index")
        if user.team.banned_at:
            return HttpResponse("必要な対応が指定日時までに完了していなかったため参加がキャンセルされました", status=403)
        if not user.team.is_active:
            return HttpResponse("このチームは無効です", status=403)
        return function(request, *args, **kwargs)

    return login_required(_function)


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
