from django.shortcuts import render
from isucon.portal.authentication.decorators import team_is_authenticated
from isucon.portal.contest.decorators import team_is_now_on_contest


@team_is_authenticated
@team_is_now_on_contest
def dashboard(request):
    return render(request, "index.html")
