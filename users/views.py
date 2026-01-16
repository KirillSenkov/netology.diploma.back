from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import ensure_csrf_cookie


@ensure_csrf_cookie
@require_GET
def csrf(request):
    return JsonResponse({'detail': 'ok'})
