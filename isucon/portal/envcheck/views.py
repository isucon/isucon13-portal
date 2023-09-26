from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from isucon.portal.authentication.decorators import envcheck_token_required


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
@require_http_methods(["POST"])
def save_result(request):
    return HttpResponse(status=204)
