from ipware import get_client_ip

from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.utils import timezone

from rest_framework.decorators import api_view

from isucon.portal.authentication.decorators import envcheck_token_required
from isucon.portal.envcheck.serializers import EnvCheckResultSerializer
from isucon.portal.contest.models import Server

@envcheck_token_required
def get_info(request):
    name = request.GET.get("name", "test")

    if not name.startswith("contest"):
        return JsonResponse({
            "name": name,
            "ami_id": settings.ENVCHECK_AMI_ID,
            "az_id": settings.ENVCHECK_AZ_ID,
        })

    return JsonResponse({
        "name": name,
        "ami_id": settings.CONTEST_AMI_ID,
        "az_id": request.team.aws_az,
    })


@csrf_exempt
@envcheck_token_required
@api_view(["POST"])
def save_result(request):
    context = {"team": request.team}
    serializer = EnvCheckResultSerializer(data=request.data, context=context)
    serializer.is_valid(raise_exception=True)
    result = serializer.save()

    if not result.name.startswith("contest"):
        if result.passed:
            request.team.envchecked_at = timezone.now()
            request.team.save(update_fields=("envchecked_at", ))
    else:
        # コンテスト
        if result.name == "contest-boot":
            if result.passed:
                # サーバ登録する
                client_addr, _ = get_client_ip(request)

                if Server.objects.of_team(request.team).count() < 3:
                    Server.objects.get_or_create(
                        team=request.team,
                        global_ip=client_addr,
                        defaults=dict(
                            hostname=client_addr,
                            private_ip=result.ip_address,
                        ),
                    )

                Server.objects.filter(
                    team=request.team,
                    global_ip=client_addr,
                ).update(is_checked=True)

    return HttpResponse(status=204)
