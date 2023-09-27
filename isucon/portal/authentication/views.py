import csv
import pglock
import urllib.parse
import requests
import datetime
import base64
import json

from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotAllowed, JsonResponse
from django.core.exceptions import PermissionDenied
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from django.urls import reverse

from isucon.portal.authentication.models import Team, RegisterCoupon, User
from isucon.portal.authentication.forms import TeamRegisterForm, JoinToTeamForm
from isucon.portal.authentication.decorators import team_is_authenticated, is_team_modify_available, is_registration_available
from isucon.portal.authentication.notify import notify_registration
from isucon.portal.authentication.forms import TeamForm, UserForm, UserIconForm

class LoginView(DjangoLoginView):
    pass


@login_required
def register(request):
    # 登録済み
    if request.user.team:
        return redirect("team_settings")

    context = {
        "is_registration_available": is_registration_available(),
        "create_team_limited": Team.objects.filter(is_guest=False).count() >= settings.MAX_TEAM_NUM,
    }
    return render(request, "register.html", context)


# @check_registration
@login_required
def create_team(request):

    # 登録済み
    if request.user.team:
        return redirect("team_settings")
    
    # 同一人物によるチームの作成は不可
    if Team.original_manager.filter(owner=request.user).exists():
        messages.warning(request, "過去にチーム作成をしたユーザーはチームの作成はできません")
        return redirect("index")


    with transaction.atomic():
        pglock.model("authentication.Team", side_effect=pglock.Return)

        coupon_token = request.GET.get("token")
        coupon = None
        if coupon_token:
            try:
                coupon = RegisterCoupon.objects.get(token=coupon_token)
            except RegisterCoupon.DoesNotExist:
                messages.warning(request, "指定されたクーポンコードは存在しません")
            else:
                if coupon.used_at:
                    messages.warning(request, "指定されたクーポンコードは利用済みです")
                    coupon = None

        # 招待チーム (スポンサー等) 以外の申し込みを制限する
        if not coupon:
            if not settings.REGISTRATION_START_AT <= timezone.now() <= settings.REGISTRATION_END_AT:
                # 登録期間
                return redirect("index")
            if Team.objects.filter(is_guest=False).count() >= settings.MAX_TEAM_NUM:
                # チーム数制限
                return render(request, "create_team_max.html")

        user = request.user
        initial = {
            "email": user.email,
        }
        form = TeamRegisterForm(request.POST or None, request.FILES or None, user=user, coupon=coupon, initial=initial)
        if request.method != "POST" or not form.is_valid():
            context = {
                'form': form,
                'username': request.user,
                'email': request.user.email,
                'coupon': coupon,
            }
            # フォームの内容が不正なら戻す
            return render(request, "create_team.html", context)

        user = form.save()

        try:
            notify_registration(user, "新しいチームが作成されました")
        except:
            pass

        return redirect("team_settings")


# @check_registration
@login_required
def join_team(request):

    # 登録済み
    if request.user.team:
        return redirect("team_settings")

    user = request.user
    initial = {}
    form = JoinToTeamForm(request.POST or None, request.FILES or None, user=user, initial=initial)

    if request.method != "POST" or not form.is_valid():
        # フォームの内容が不正なら戻す
        return render(request, "join_team.html", {'form': form, 'username': request.user})

    user = form.save()

    try:
        notify_registration(user, "チームにメンバーが追加されました")
    except:
        pass

    return redirect("team_settings")


@team_is_authenticated
def team_settings(request):
    form = TeamForm(instance=request.user.team)
    user_form = UserForm(instance=request.user)

    if request.method == "POST" and not is_team_modify_available():
        messages.error(request, "チーム情報の変更期間を過ぎています")
        return redirect("team_settings")

    if request.method == "POST" and request.POST.get("action") == "team":
        form = TeamForm(request.POST, instance=request.user.team)
        if form.is_valid():
            form.save()
            messages.success(request, "チーム情報を更新しました")
            return redirect("team_settings")

    if request.method == "POST" and request.POST.get("action") == "user":
        user_form = UserForm(request.POST, instance=request.user)
        if user_form.is_valid():
            user_form.save()
            messages.success(request, "ユーザー情報を更新しました")
            return redirect("team_settings")

    context = {
        "form": form,
        "user_form": user_form,
        "team_members": request.user.team.user_set.all()
    }
    return render(request, "team_settings.html", context)

@team_is_authenticated
def update_user_icon(request):
    form = UserIconForm(user=request.user)
    if request.method == "POST":
        form = UserIconForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "ユーザーのアイコンを更新しました")
        else:
            messages.warning(request, "ユーザーのアイコンを更新に失敗しました")
    else:
        return HttpResponseNotAllowed(["POST"])

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse(
            {}, status = 200
        )
    return redirect("team_settings")


@team_is_authenticated
def decline(request):
    if not is_team_modify_available():
        messages.error(request, "チーム情報の変更期間を過ぎています")
        return redirect("team_settings")

    if request.user.team.owner != request.user:
        messages.warning(request, "リーダーのみがチームの辞退操作ができます")
        return redirect("team_settings")

    if request.method == "POST":
        if request.POST.get("action") == "decline":
            request.user.team.decline()
            messages.success(request, "チーム登録を辞退しました")
            return redirect("index")

    context = {
    }
    return render(request, "team_decline.html", context)


@team_is_authenticated
def cloudformation_envcheck(request):
    team = request.user.team
    
    authorized_keys = []
    for user in User.objects.filter(team=team):
        authorized_keys.append(user.authorized_keys)
    authorized_keys = "\n".join(authorized_keys)

    portal_credentials = {
        "dev": settings.ENVCHECK_DEVELOP,
        "token": team.envcheck_token,
        "host": request.META.get("HTTP_HOST"),
    }

    context = {
        "az_id": settings.ENVCHECK_AZ_ID,
        "ami_id": settings.ENVCHECK_AMI_ID,
        "authorized_keys": base64.b64encode(authorized_keys.encode("utf-8")).decode("ascii"),
        "portal_credentials": base64.b64encode(json.dumps(portal_credentials).encode("utf-8")).decode("ascii"),
    }

    response = render(request, "cloudformation_envcheck.yaml", context)
    response['Content-Disposition'] = 'attachment; filename="cloudformation_envcheck.yaml"'
    return response


def team_list(request):
    teams = Team.objects.order_by("id").prefetch_related("user_set")
    context = {"teams": teams}

    return render(request, "team_list.html", context)

def team_list_csv(request):
    teams = Team.objects.order_by("id").prefetch_related("user_set")

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="teams.csv"'
    writer = csv.writer(response)

    for team in teams:
        row = [team.name]
        for u in team.user_set.all():
            row.append(u.display_name)
        writer.writerow(row)

    return response

@login_required
def discord_oauth_begin(request):
    if not request.user.team:
        raise PermissionDenied

    state = "state"
    params = {
        "client_id": settings.DISCORD_OAUTH_CLIENT_ID,
        "redirect_uri": request.build_absolute_uri(reverse("discord_oauth_complete")),
        "response_type": "code",
        "scope": "identify guilds.join",
        "state": state,
    }
    url = "https://discord.com/api/oauth2/authorize?{}".format(urllib.parse.urlencode(params))
    request.session["DISCORD_STATE"] = state
    return redirect(url)


@login_required
def discord_oauth_complete(request):
    code = request.GET.get("code")
    state = request.GET.get("state")
    expected_state = request.session.get("DISCORD_STATE", None)

    if not all([code, state, expected_state]) or state != expected_state:
        return redirect("discord_oauth_begin")
    del request.session["DISCORD_STATE"]

    data = {
        'client_id': settings.DISCORD_OAUTH_CLIENT_ID,
        'client_secret': settings.DISCORD_OAUTH_CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': request.build_absolute_uri(reverse("discord_oauth_complete")),
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    r = requests.post("https://discord.com/api/oauth2/token", data=data, headers=headers)
    r.raise_for_status()
    data = r.json()
    print(data)

    request.user.discord_access_token = data["access_token"]
    request.user.discord_refresh_token = data["refresh_token"]
    request.user.discord_expired_at = timezone.now() + datetime.timedelta(seconds=data["expires_in"])
    request.user.join_discord()
    request.user.update_discord()

    messages.success(request, "Discordアカウントを接続しました")

    return redirect("team_settings")
