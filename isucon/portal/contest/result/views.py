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

    top_teams = Score.objects.passed()[:30]

    context.update({
        "top_teams": top_teams,
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
