import base64
import json
import datetime

from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.utils import timezone

from isucon.portal import utils as portal_utils
from isucon.portal.authentication.decorators import team_is_authenticated
from isucon.portal.authentication.models import Team, User
from isucon.portal.contest.decorators import team_is_now_on_contest
from isucon.portal.contest.models import Server, Job, Score
from isucon.portal.contest.redis.color import iter_colors
from isucon.portal.contest.redis.client import TeamGraphData

from isucon.portal.contest.forms import ServerTargetForm

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

    context.update({
        "servers": servers,
    })
    return render(request, "servers.html", context)

@team_is_authenticated
@team_is_now_on_contest
def cloudformation_contest(request):
    team = request.user.team

    authorized_keys = []
    for user in User.objects.filter(team=team):
        authorized_keys.append(user.authorized_keys)
    authorized_keys = "\n".join(authorized_keys)

    portal_credentials = {
        "dev": False,
        "token": team.envcheck_token,
        "host": request.META.get("HTTP_HOST"),
    }

    context = {
        "az_id": settings.CONTEST_AZ_ID,
        "ami_id": settings.CONTEST_AMI_ID,
        "authorized_keys": base64.b64encode(authorized_keys.encode("utf-8")).decode("ascii"),
        "portal_credentials": base64.b64encode(json.dumps(portal_credentials).encode("utf-8")).decode("ascii"),
    }

    response = render(request, "cloudformation_contest.yaml", context)
    response['Content-Disposition'] = 'attachment; filename="cloudformation_contest.yaml"'
    return response


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



def get_graph_data():
    color_iterator = iter_colors()
    datasets = []

    # NOTE: 最後の1時間のデータは含まない
    graph_end_at = datetime.datetime.combine(settings.CONTEST_DATE, settings.CONTEST_END_TIME) - datetime.timedelta(hours=1)
    graph_end_at = graph_end_at.replace(tzinfo=portal_utils.jst)

    for team in Team.objects.filter(is_active=True):
        team_graph_data = TeamGraphData(team)
        for job in Job.objects.filter(status=Job.DONE, team=team, finished_at__lt=graph_end_at).order_by('finished_at').select_related("team"):
            team_graph_data.append(job)

        # グラフの彩色
        color, hover_color = next(color_iterator)
        team_graph_data.assign_color(color, hover_color)

        # 全てのグラフデータを取得
        datasets.append(team_graph_data.to_dict(partial=False))

    return datasets


def graph(request):
    # NOTE: CONTEST_START_TIME-10minutes ~ CONTEST_END_TIME+10minutes にするようにmin, maxを渡す
    graph_start_at = datetime.datetime.combine(settings.CONTEST_DATE, settings.CONTEST_START_TIME) - datetime.timedelta(minutes=10)
    graph_start_at = graph_start_at.replace(tzinfo=portal_utils.jst)

    graph_end_at = datetime.datetime.combine(settings.CONTEST_DATE, settings.CONTEST_END_TIME) + datetime.timedelta(minutes=10)
    graph_end_at = graph_end_at.replace(tzinfo=portal_utils.jst)

    graph_datasets = get_graph_data()

    data = {
        'graph_datasets': graph_datasets,
        "graph_min": portal_utils.normalize_for_graph_label(graph_start_at),
        "graph_max": portal_utils.normalize_for_graph_label(graph_end_at),
    }

    return JsonResponse(
        data,
        status=200,
        headers={
            "Cache-Control": "public, max-age=60, s-maxage=60",
        },
    )

