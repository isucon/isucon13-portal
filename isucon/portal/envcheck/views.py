from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from isucon.portal.authentication.decorators import envcheck_token_required


@envcheck_token_required
def get_info(request):
    name = request.GET.get("name", "test")
    return JsonResponse({
        "name": name,
        "ami_id": "",
        "az_id": "",
    })


@envcheck_token_required
@require_http_methods(["POST"])
def save_result(request):
    pass
