from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .ussd_logic import ussd_menu


@csrf_exempt
@require_POST
def ussd_callback(request):
    phone = request.POST.get("phoneNumber", "")
    text = request.POST.get("text", "")
    return HttpResponse(ussd_menu(phone, text), content_type="text/plain")
