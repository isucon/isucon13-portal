import datetime
from dateutil.parser import parse as parse_datetime

from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from isucon.portal.contest.redis.color import iter_colors
from django.db.models import F, OuterRef, Func, Subquery


from isucon.portal.authentication.models import Team, User
from isucon.portal.contest.models import Job, Score
from isucon.portal import utils as portal_utils
from isucon.portal.contest.redis.client import TeamGraphData

def get_base_context(user):
    return {
        "staff": True,
    }

def get_participate_at(request):
    """セッションに格納された日付文字列を取得する"""
    if 'participate_at' in request.session:
        participate_at_str = request.session.get('participate_at')
    else:
        return datetime.date.today()

    try:
        return parse_datetime(participate_at_str).date()
    except ValueError:
        return datetime.date.today()

def store_graph_params(request):
    """セッションにグラフ表示パラメータを設定する"""
    # participate_at(グラフが認識する日付) の設定
    # NOTE: 日時型がJSON Serializableでないので、文字列として一旦格納し、取得時に変換するようにする
    if 'participate_at' in request.GET:
        participate_at_str = request.GET.get('participate_at', '')
    else:
        participate_at_str = request.session.get('participate_at', '')

    request.session['participate_at'] = participate_at_str

    # graph_teams(グラフに表示するチームの数) の設定
    try:
        if 'graph_teams' in request.GET:
            graph_teams_str = request.GET.get("graph_teams", settings.RANKING_TOPN)
        else:
            graph_teams_str = request.session.get('graph_teams', '')
        graph_teams = int(graph_teams_str)
    except ValueError:
        graph_teams = settings.RANKING_TOPN

    request.session['graph_teams'] = graph_teams

@staff_member_required
def dashboard(request):
    context = get_base_context(request.user)
    store_graph_params(request)

    participate_at = get_participate_at(request)
    print("participate_at: type={}, value={}".format(type(participate_at), participate_at))

    top_teams = Score.objects.passed()[:30]

    context.update({
        "top_teams": top_teams,
    })

    return render(request, "staff/dashboard.html", context)



@staff_member_required
def scores(request):
    context = get_base_context(request.user)
    store_graph_params(request)

    participate_at = get_participate_at(request)

    context.update({
        "passed": Score.objects.passed(),
        "failed": Score.objects.failed(),
    })

    return render(request, "staff/scores.html", context)


@staff_member_required
def jobs(request):
    context = get_base_context(request.user)

    def paginate_query(request, queryset, count):
        paginator = Paginator(queryset, count)
        page = request.GET.get('page', "1")
        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        return page_obj

    page = paginate_query(request, Job.objects.order_by("-id"), 50)

    show_pages = []
    for n in page.paginator.page_range:
        if n <= 3 or (page.paginator.num_pages-3) < n:
            show_pages.append(n)
        elif page.number - 2 < n < page.number + 2:
            show_pages.append(n)
        elif n == 4:
            show_pages.append(None)
        elif page.number - 2 == n or n == page.number + 2:
            if show_pages[-1]:
                show_pages.append(None)

    context.update({
        "jobs": page,
        "page_obj": page,
        "show_pages": show_pages,
    })

    return render(request, "staff/jobs.html", context)


@staff_member_required
def job_detail(request, pk):
    context = get_base_context(request.user)

    job = get_object_or_404(Job, pk=pk)
    context.update({
        "job": job,
    })

    return render(request, "staff/job_detail.html", context)

def get_graph_data():
    color_iterator = iter_colors()
    datasets = []

    graph_end_at = datetime.datetime.combine(settings.CONTEST_DATE, settings.CONTEST_END_TIME) + datetime.timedelta(minutes=10)
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


@staff_member_required
def graph(request):
    # NOTE: CONTEST_START_TIME-10minutes ~ CONTEST_END_TIME+10minutes にするようにmin, maxを渡す
    graph_start_at = datetime.datetime.combine(settings.CONTEST_DATE, settings.CONTEST_START_TIME) - datetime.timedelta(minutes=10)
    graph_start_at = graph_start_at.replace(tzinfo=portal_utils.jst)

    graph_end_at = datetime.datetime.combine(settings.CONTEST_DATE, settings.CONTEST_END_TIME) + datetime.timedelta(minutes=10)
    graph_end_at = graph_end_at.replace(tzinfo=portal_utils.jst)

    graph_datasets = get_graph_data()

    # ランキング情報

    student_count_subquery = User.objects.filter(
        team_id=OuterRef("team_id"), 
        is_student=True,
    ).order_by().annotate(student_count=Func(F('id'), function='Count')).values('student_count')

    scores = Score.objects.annotate(
            student_count=Subquery(student_count_subquery),
    ).filter(team__is_active=True).select_related("team").order_by("-latest_score")


    ranking = [
        {
            "team": {
                "id": score.team.id,
                "name": score.team.name,
                "has_student": score.student_count > 0,
                "is_guest": score.team.is_guest,
            },
            "latest_score": score.latest_score,
            "rank": rank,
        } for rank, score in enumerate(scores, start=1)
    ]
    data = {
        'graph_datasets': graph_datasets,
        "graph_min": portal_utils.normalize_for_graph_label(graph_start_at),
        "graph_max": portal_utils.normalize_for_graph_label(graph_end_at),
        "ranking": ranking,
    }

    return JsonResponse(
        data,
        status=200,
        headers={
            "Cache-Control": "public, max-age=60, s-maxage=60",
        },
    )


