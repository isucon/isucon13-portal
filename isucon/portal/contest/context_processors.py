from django.conf import settings
from django.utils import timezone

from isucon.portal.authentication.decorators import is_registration_available, is_team_modify_available
# from isucon.portal.contest.models import Server, Information

def settings_url(request):
    is_now_on_contest = False
    context = {
        'discord_url': settings.DISCORD_URL,
        'manual_url': settings.MANUAL_URL,
        'isucon_official_url': settings.ISUCON_OFFICIAL_URL,
        'regulation_url': settings.REGULATION_URL,
        'twitter_url': settings.TWITTER_URL,
        'term_url': settings.TERM_URL,
        'registration_start_at': settings.REGISTRATION_START_AT,
        'registration_end_at': settings.REGISTRATION_END_AT,
        'team_modify_end_at': settings.TEAM_MODIFY_END_AT,
        'is_registration_available': is_registration_available(),
        'is_team_modify_available': is_team_modify_available(),
        'is_now_on_contest': False,
        'informations': [],
        'show_result_enabled': settings.SHOW_RESULT_AFTER <= timezone.now(),
        'discord_server_id': settings.DISCORD_SERVER_ID,
    }


    if request.user.is_authenticated and request.user.team is not None:
        team = request.user.team
        team_context = {
            "is_now_on_contest": team.is_playing(),
            "servers": [], # FIXME: Server.objects.of_team(team),
            'informations': [] # FIXME: Information.objects.of_team(team),
        }

        if request.user.is_staff:
            team_context["is_now_on_contest"] = True

        team_context["is_now_on_contest"] = False  # FIXME: remove
        context.update(team_context)


    return context
