import os
from pathlib import Path
import uuid
import json

from django.conf import settings
from django.http import (
    HttpRequest,
    JsonResponse,
    HttpResponseNotAllowed,
    FileResponse
)
from django.utils import timezone
from django.views.decorators.http import (
    require_POST,
    require_GET,
    require_http_methods
)

from .models import File
from .services import (
    make_stored_name,
    user_storage_abs_path,
    write_file,
    get_file_for_user,
    can_manage_files,
    ensure_user_storage_dir
)

from users.models import User

@require_POST
def upload_file(request):
    if not request.user.is_authenticated:
        return JsonResponse({'detail': 'Authentication required'}, status=401)

    uploaded_file = request.FILES.get('file')
    if not uploaded_file:
        return JsonResponse({'detail': 'Missing file'}, status=400)

    ensure_user_storage_dir(request.user.storage_rel_path)

    comment = request.POST.get('comment') or None

    stored_name = make_stored_name(uploaded_file.name)
    rel_dir = request.user.storage_rel_path
    abs_path = user_storage_abs_path(rel_dir) / stored_name

    write_file(uploaded_file, abs_path)

    obj = File.objects.create(
        owner=request.user,
        original_name=uploaded_file.name,
        stored_name=stored_name,
        relative_path=str(rel_dir) + stored_name,
        size_bytes=uploaded_file.size,
        comment=comment,
        uploaded=timezone.now(),
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

    user_id = request.GET.get('user_id')

    if user_id is not None:
        if not user_id.isdigit():
            return JsonResponse({'detail': 'Invalid user_id: expected integer'}, status=400)

        target_user = User.objects.filter(id=int(user_id)).first()
        if not target_user:
            return JsonResponse({'detail': 'User not found'}, status=404)

        if not can_manage_files(request.user, target_user):
            return JsonResponse({'detail': 'Forbidden'}, status=403)

        files = File.objects.filter(owner_id=int(user_id))
    else:
        files = File.objects.filter(owner=request.user)

    files = files.order_by('-uploaded')

    data = [
        {
            'id': f.id,
            'original_name': f.original_name,
            'size_bytes': f.size_bytes,
            'comment': f.comment,
            'uploaded': f.uploaded.isoformat(),
            'last_downloaded': f.last_downloaded.isoformat() if f.last_downloaded else None,
            'share_url': request.build_absolute_uri(f'/api/share/{f.share_token}/') if f.share_token else None,
            'share_created': f.share_created.isoformat() if f.share_created else None,
        }
        for f in files
    ]
    return JsonResponse(data, safe=False)

@require_http_methods(['DELETE'])
def delete_file(request, file_id):
    if not request.user.is_authenticated:
        return JsonResponse({'detail': 'Authentication required'}, status=401)

    file_obj = get_file_for_user(request, file_id)
    if not file_obj:
        return JsonResponse({'detail': 'File not found'}, status=404)

    full_path = user_storage_abs_path(file_obj.relative_path)
    if full_path.exists():
        full_path.unlink()

    file_obj.delete()

    return JsonResponse({'detail': 'File deleted'})

@require_http_methods(['PATCH'])
def rename_file(request, file_id):
    if not request.user.is_authenticated:
        return JsonResponse({'detail': 'Authentication required'}, status=401)

    file_obj = get_file_for_user(request, file_id)
    if not file_obj:
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

@require_GET
def download_file(request, file_id):
    if not request.user.is_authenticated:
        return JsonResponse({'detail': 'Authentication required'}, status=401)

    file_obj = get_file_for_user(request, file_id)
    if not file_obj:
        return JsonResponse({'detail': 'File not found'}, status=404)

    full_path = user_storage_abs_path(file_obj.relative_path)
    if not full_path.exists():
        return JsonResponse({'detail': 'File not found'}, status=404)

    mode = request.GET.get('mode', 'download')
    as_attachment = mode != 'preview'

    file_obj.last_downloaded = timezone.now()
    file_obj.save(update_fields=['last_downloaded'])

    return FileResponse(
        full_path.open('rb'),
        as_attachment=as_attachment,
        filename=file_obj.original_name,
    )

@require_http_methods(['PATCH'])
def comment_file(request, file_id):
    if not request.user.is_authenticated:
        return JsonResponse({'detail': 'Authentication required'}, status=401)

    file_obj = get_file_for_user(request, file_id)
    if not file_obj:
        return JsonResponse({'detail': 'File not found'}, status=404)

    try:
        payload = json.loads(request.body.decode('utf-8') or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'detail': 'Invalid JSON'}, status=400)

    # comment может быть пустой строкой — разрешим очистку
    if 'comment' not in payload:
        return JsonResponse({'detail': 'Missing comment'}, status=400)

    file_obj.comment = payload.get('comment')
    file_obj.save(update_fields=['comment'])

    return JsonResponse({
        'id': file_obj.id,
        'comment': file_obj.comment,
    })

@require_http_methods(['POST']) # т.к. это действие по смыслу,
                                # а не просто UPDSTE
def enable_share(request, file_id):
    if not request.user.is_authenticated:
        return JsonResponse({'detail': 'Authentication required'}, status=401)

    file_obj = get_file_for_user(request, file_id)
    if not file_obj:
        return JsonResponse({'detail': 'File not found'}, status=404)

    if not file_obj.share_token:
        file_obj.share_token = uuid.uuid4()
        file_obj.share_created = timezone.now()
        file_obj.save(update_fields=['share_token', 'share_created'])

    url = request.build_absolute_uri(f'/api/share/{file_obj.share_token}/')

    return JsonResponse({
        'id': file_obj.id,
        'share_url': url,
        'share_created': file_obj.share_created.isoformat() if file_obj.share_created else None,
        'share_token': str(file_obj.share_token),
    })

@require_http_methods(['POST']) # т.к. это действие по смыслу,
                                # а не просто UPDSTE
def disable_share(request, file_id):
    if not request.user.is_authenticated:
        return JsonResponse({'detail': 'Authentication required'}, status=401)

    file_obj = get_file_for_user(request, file_id)
    if not file_obj:
        return JsonResponse({'detail': 'File not found'}, status=404)

    file_obj.share_token = None
    file_obj.share_created = None
    file_obj.save(update_fields=['share_token', 'share_created'])

    return JsonResponse({
        'id': file_obj.id,
        'share_url': None,
        'share_created': None,
        'share_token': None,
    })

@require_http_methods(['GET'])
def download_shared(request, token):
    try:
        file_obj = File.objects.get(share_token=token)
    except File.DoesNotExist:
        return JsonResponse({'detail': 'File not found'}, status=404)

    full_path = user_storage_abs_path(file_obj.relative_path)
    if not full_path.exists():
        return JsonResponse({'detail': 'File not found'}, status=404)

    file_obj.last_downloaded = timezone.now()
    file_obj.save(update_fields=['last_downloaded'])

    return FileResponse(
        full_path.open('rb'),
        as_attachment=True,
        filename=file_obj.original_name,
    )
