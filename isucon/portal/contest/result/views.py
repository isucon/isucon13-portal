import datetime

from django.shortcuts import render, get_object_or_404
from django.conf import settings

from isucon.portal.authentication.decorators import team_is_authenticated
from isucon.portal.contest.decorators import show_result_enabled
from isucon.portal.contest.models import Job, Score
from isucon.portal import utils as portal_utils
from isucon.portal.contest.redis.client import RedisClient

def get_base_context(user):
    return {
        "result": True,
        "staff": False,
    }


@team_is_authenticated
@show_result_enabled
def dashboard(request):
    context = get_base_context(request.user)
    participate_at = request.user.team.participate_at

    # NOTE: team.participate_at の日付の、CONTEST_START_TIME-10minutes ~ CONTEST_END_TIME+10minutes にするようにmin, maxを渡す
    graph_start_at = datetime.datetime.combine(participate_at, settings.CONTEST_START_TIME) - datetime.timedelta(minutes=10)
    graph_start_at = graph_start_at.replace(tzinfo=portal_utils.jst)

    graph_end_at = datetime.datetime.combine(participate_at, settings.CONTEST_END_TIME) + datetime.timedelta(minutes=10)
    graph_end_at = graph_end_at.replace(tzinfo=portal_utils.jst)

    try:
        top_n = int(request.GET.get("graph_teams", settings.RANKING_TOPN))
    except ValueError:
        top_n = settings.RANKING_TOPN

    top_teams = Score.objects.passed()[:30]

    """
    # topN チームID配列を用意
    ranking = [row["team__id"] for row in
                Score.objects.passed().values("team__id")[:top_n]]

    if request.user.team.id not in top_teams:
        ranking.append(request.user.team.id)
    """
    ranking = [request.user.team.id]


    # キャッシュ済みグラフデータの取得 (topNのみ表示するデータ)
    client = RedisClient()
    graph_labels, graph_datasets = client.get_graph_data_for_staff(participate_at, ranking)

    context.update({
        "top_teams": top_teams,
        "graph_min_label": portal_utils.normalize_for_graph_label(graph_start_at),
        "graph_max_label": portal_utils.normalize_for_graph_label(graph_end_at),
        "graph_labels": graph_labels,
        "graph_datasets": graph_datasets,
    })

    return render(request, "result/dashboard.html", context)



@team_is_authenticated
@show_result_enabled
def scores(request):
    context = get_base_context(request.user)

    context.update({
        "passed": Score.objects.passed().filter(team__owner__is_active=True).select_related("team"),
        "failed": Score.objects.failed().filter(team__owner__is_active=True).select_related("team"),
    })

    return render(request, "scores.html", context)

@team_is_authenticated
@show_result_enabled
def jobs(request):
    context = get_base_context(request.user)

    jobs = Job.objects.of_team(request.user.team)
    context.update({
        "jobs": jobs,
    })

    return render(request, "jobs.html", context)

@team_is_authenticated
@show_result_enabled
def job_detail(request, pk):
    context = get_base_context(request.user)

    job = get_object_or_404(Job.objects.filter(team=request.user.team), pk=pk)
    context.update({
        "job": job,
    })

    return render(request, "job_detail.html", context)
