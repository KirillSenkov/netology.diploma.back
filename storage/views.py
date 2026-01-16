import os
import json

from django.shortcuts import render
from django.http import JsonResponse, HttpResponseNotAllowed
from django.views.decorators.http import require_POST, require_GET, require_http_methods
from django.utils import timezone

from .models import File
from .services import make_stored_name, user_storage_dir, write_file


@require_POST
def upload_file(request):
    if not request.user.is_authenticated:
        return JsonResponse({'detail': 'Authentication required'}, status=401)

    uploaded_file = request.FILES.get('file')
    if not uploaded_file:
        return JsonResponse({'detail': 'Missing file'}, status=400)

    comment = request.POST.get('comment') or None

    stored_name = make_stored_name(uploaded_file.name)
    rel_dir = request.user.storage_rel_path
    abs_path = user_storage_dir(rel_dir) / stored_name

    write_file(uploaded_file, abs_path)

    obj = File.objects.create(
        owner=request.user,
        original_name=uploaded_file.name,
        stored_name=stored_name,
        relative_path=str(rel_dir) + stored_name,
        size_bytes=uploaded_file.size,
        comment=comment,
        uploaded=timezone.now(),  # на самом деле auto_now_add сам проставит, но ок
    )

    return JsonResponse(
        {
            'id': obj.id,
            'original_name': obj.original_name,
            'size_bytes': obj.size_bytes,
            'comment': obj.comment,
            'uploaded': obj.uploaded.isoformat(),
        },
        status=201,
    )

@require_GET
def list_files(request):
    if not request.user.is_authenticated:
        return JsonResponse({'detail': 'Authentication required'}, status=401)

    files = File.objects.filter(owner=request.user).order_by('-uploaded')

    data = [
        {
            'id': f.id,
            'original_name': f.original_name,
            'size_bytes': f.size_bytes,
            'comment': f.comment,
            'uploaded': f.uploaded.isoformat(),
        }
        for f in files
    ]

    return JsonResponse(data, safe=False)

@require_http_methods(['DELETE'])
def delete_file(request, file_id):
    if request.method != 'DELETE':
        return HttpResponseNotAllowed(['DELETE'])

    if not request.user.is_authenticated:
        return JsonResponse({'detail': 'Authentication required'}, status=401)

    try:
        file_obj = File.objects.get(id=file_id, owner=request.user)
    except File.DoesNotExist:
        return JsonResponse({'detail': 'File not found'}, status=404)

    abs_path = file_obj.relative_path
    full_path = os.path.join(os.getcwd(), 'storage_data', abs_path)

    if os.path.exists(full_path):
        os.remove(full_path)

    file_obj.delete()

    return JsonResponse({'detail': 'File deleted'})

@require_http_methods(['PATCH'])
def rename_file(request, file_id):
    if not request.user.is_authenticated:
        return JsonResponse({'detail': 'Authentication required'}, status=401)

    try:
        file_obj = File.objects.get(id=file_id, owner=request.user)
    except File.DoesNotExist:
        return JsonResponse({'detail': 'File not found'}, status=404)

    try:
        payload = json.loads(request.body.decode('utf-8') or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'detail': 'Invalid JSON'}, status=400)

    new_name = payload.get('name')
    if not new_name:
        return JsonResponse({'detail': 'Missing name'}, status=400)

    file_obj.original_name = new_name
    file_obj.save(update_fields=['original_name'])

    return JsonResponse({
        'id': file_obj.id,
        'original_name': file_obj.original_name,
    })


