import csv

from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotAllowed, JsonResponse
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.contrib import messages

from isucon.portal.authentication.models import Team
from isucon.portal.authentication.forms import TeamRegisterForm, JoinToTeamForm
from isucon.portal.authentication.decorators import team_is_authenticated, check_registration
from isucon.portal.authentication.notify import notify_registration
from isucon.portal.authentication.forms import TeamForm, UserForm, UserIconForm

class LoginView(DjangoLoginView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["create_team_limited"] = Team.objects.count() >= settings.MAX_TEAM_NUM
        return context


@check_registration
@login_required
def create_team(request):

    if Team.objects.count() >= settings.MAX_TEAM_NUM:
        return render(request, "create_team_max.html")

    user = request.user
    initial = {
        "email": user.email,
    }
    form = TeamRegisterForm(request.POST or None, request.FILES or None, user=user, initial=initial)
    if not form.is_valid():
        # フォームの内容が不正なら戻す
        return render(request, "create_team.html", {'form': form, 'username': request.user, 'email': request.user.email})

    form.save()

    try:
        notify_registration()
    except:
        pass

    return redirect("team_settings")

@check_registration
@login_required
def join_team(request):
    user = request.user
    initial = {}
    form = JoinToTeamForm(request.POST or None, request.FILES or None, user=user, initial=initial)

    if not form.is_valid():
        # フォームの内容が不正なら戻す
        return render(request, "join_team.html", {'form': form, 'username': request.user})

    form.save()

    try:
        notify_registration()
    except:
        pass

    return redirect("team_settings")


@team_is_authenticated
def team_settings(request):
    form = TeamForm(instance=request.user.team)
    user_form = UserForm(instance=request.user)
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
