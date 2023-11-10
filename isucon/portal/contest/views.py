from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseNotAllowed, HttpResponse, JsonResponse
from django.utils import timezone

from isucon.portal import utils as portal_utils
from isucon.portal.authentication.decorators import team_is_authenticated
from isucon.portal.authentication.models import Team
from isucon.portal.contest.decorators import team_is_now_on_contest
from isucon.portal.contest.models import Server, Job, Score

from isucon.portal.contest.forms import ServerTargetForm, ServerAddForm
from isucon.portal.contest.redis.client import RedisClient


def get_base_context(user):
    try:
        target_server = Server.objects.get_bench_target(user.team)
    except Server.DoesNotExist:
        # FIXME: チーム作成直後、チームのサーバは存在しないため、ここでDoesNotExistが投げられるのを回避するためのコード
        # チームにサーバを割り当てる時どうするか決める
        target_server = None

    is_last_spurt = portal_utils.is_last_spurt(timezone.now(), user.team.participate_at)

    return {
        "staff": False,
        "target_server": target_server,
        "is_last_spurt": is_last_spurt
    }

@team_is_authenticated
@team_is_now_on_contest
def dashboard(request):
    context = get_base_context(request.user)

    recent_jobs = Job.objects.of_team(team=request.user.team).order_by("-created_at")[:10]
    top_teams = Score.objects.passed().select_related("team")[:30]

    # チームのスコアを取得
    try:
        team = Score.objects.get(team=request.user.team)
        team_score = team.latest_score
    except:
        Score.objects.create(team=request.user.team)
        team = Score.objects.get(team=request.user.team)
        team_score = team.latest_score

    context.update({
        "recent_jobs": recent_jobs,
        "top_teams": top_teams,
        "team_score": team_score
    })

    return render(request, "dashboard.html", context)

@team_is_authenticated
@team_is_now_on_contest
def jobs(request):
    context = get_base_context(request.user)

    jobs = Job.objects.of_team(request.user.team)
    context.update({
        "jobs": jobs,
    })

    return render(request, "jobs.html", context)

@team_is_authenticated
@team_is_now_on_contest
def job_detail(request, pk):
    context = get_base_context(request.user)

    job = get_object_or_404(Job.objects.filter(team=request.user.team), pk=pk)
    context.update({
        "job": job,
    })

    return render(request, "job_detail.html", context)

@team_is_authenticated
@team_is_now_on_contest
def job_enqueue(request):

    if not request.headers.get("x-requested-with") == "XMLHttpRequest":
        return HttpResponse("このエンドポイントはAjax専用です", status=400)

    context = get_base_context(request.user)

    # サーバの設定チェック
    if not Server.objects.of_team(request.user.team).exists():
        return JsonResponse(
            {"error": "サーバが設定されていません"}, status = 409
        )

    job = None
    try:
        job = Job.objects.enqueue(request.user.team)
    except Job.DuplicateJobError:
        return JsonResponse(
            {"error": "実行中のジョブがあります"}, status = 409
        )

    data = {
        "id": job.id,
    }

    return JsonResponse(
        data, status = 200
    )


@team_is_authenticated
@team_is_now_on_contest
def scores(request):
    context = get_base_context(request.user)

    context.update({
        "passed": Score.objects.passed().select_related("team"),
        "failed": Score.objects.failed().select_related("team"),
    })

    return render(request, "scores.html", context)

@team_is_authenticated
@team_is_now_on_contest
def servers(request):
    context = get_base_context(request.user)
    servers = Server.objects.of_team(request.user.team)
    add_form = ServerAddForm(team=request.user.team)

    if request.method == "POST":
        action = request.POST.get("action", "").lower()

        if action == "target":
            form = ServerTargetForm(request.POST, team=request.user.team)
            if form.is_valid():
                server = form.save()
                if Server.objects.of_team(request.user.team).count() == 1:
                    Server.objects.of_team(request.user.team).update(is_bench_target=True)
                messages.success(request, "ベンチマーク対象のサーバを変更しました")
                return redirect("servers")

        if action == "add":
            add_form = ServerAddForm(request.POST, team=request.user.team)
            if add_form.is_valid():
                add_form.save()
                messages.success(request, "サーバを追加しました")
                return redirect("servers")

    context.update({
        "servers": servers,
        "add_form": add_form
    })
    return render(request, "servers.html", context)


@team_is_authenticated
@team_is_now_on_contest
def delete_server(request, pk):
    if request.method != "DELETE":
        return HttpResponseNotAllowed(["DELETE"])

    server = get_object_or_404(Server.objects.of_team(request.user.team), pk=pk)

    if server.is_bench_target:
        messages.warning(request, "ベンチマーク対象のサーバは削除できません")
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return HttpResponse("Error")
        return redirect("servers")

    server.delete()

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse(
            {}, status = 200
        )

    messages.success(request, "サーバを削除しました")
    return redirect("servers")


@team_is_authenticated
@team_is_now_on_contest
def teams(request):

    teams = Team.objects.order_by('id').all()

    paginator = Paginator(teams, 100)

    try:
        page_index = int(request.GET.get('page', 1))
    except ValueError:
        page_index = 1

    teams = paginator.get_page(page_index)

    context = {
        'teams': teams,
    }

    return render(request, "teams.html", context)


@team_is_authenticated
@team_is_now_on_contest
def graph(request):
    if not request.headers.get("x-requested-with") == "XMLHttpRequest":
        return HttpResponse("このエンドポイントはAjax専用です", status=400)

    context = get_base_context(request.user)
    team = request.user.team

    ranking = [row["team__id"] for row in
                    Score.objects.passed().values("team__id")[:settings.RANKING_TOPN]]

    client = RedisClient()
    graph_datasets, graph_min, graph_max = client.get_graph_data(team, ranking, is_last_spurt=context['is_last_spurt'])

    data = {
        'graph_datasets': graph_datasets,
        'graph_min': graph_min,
        'graph_max': graph_max,
    }

    return JsonResponse(
        data, status = 200
    )

