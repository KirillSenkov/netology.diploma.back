from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from .models import File
from .services import make_stored_name, user_storage_dir, write_file


@csrf_exempt
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



