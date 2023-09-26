from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from rest_framework.decorators import api_view

from isucon.portal.authentication.decorators import envcheck_token_required
from isucon.portal.envcheck.serializers import EnvCheckResultSerializer

@envcheck_token_required
def get_info(request):
    name = request.GET.get("name", "test")
    return JsonResponse({
        "name": name,
        "ami_id": settings.ENVCHECK_AMI_ID,
        "az_id": settings.ENVCHECK_AZ_ID,
    })


@csrf_exempt
@envcheck_token_required
@api_view(["POST"])
def save_result(request):
    context = {"team": request.team}
    serializer = EnvCheckResultSerializer(data=request.data, context=context)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return HttpResponse(status=204)
