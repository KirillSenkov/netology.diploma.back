from json import loads, JSONDecodeError
from re import compile as make_regex
from uuid import uuid4

from django.contrib.auth import authenticate, login, logout
from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import (
    require_GET,
    require_POST,
    require_http_methods
)
from django.views.decorators.csrf import ensure_csrf_cookie

from .models import User
from storage.services import user_storage_abs_path, ensure_user_storage_dir
from .services import (
    get_user_rank,
    get_user_level,
    can_manage_user,
    can_delete_user,
    can_change_level,
    set_user_level
)
USERNAME_RE = make_regex(r'^[A-Za-z][A-Za-z0-9]{3,19}$')
EMAIL_RE = make_regex(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')
@ensure_csrf_cookie
@require_GET
def csrf(request: HttpRequest) -> JsonResponse:
    return JsonResponse({'detail': 'ok'})

def validate_password(pw: str) -> list[str]:
    errors: list[str] = []
    if pw is None:
        return ['Password is required']

    if len(pw) < 6:
        errors.append('Password must be at least 6 characters')

    if not any(ch.isupper() for ch in pw):
        errors.append('Password must contain at least one uppercase letter')

    if not any(ch.isdigit() for ch in pw):
        errors.append('Password must contain at least one digit')

    if not any(not ch.isalnum() for ch in pw):
        errors.append('Password must contain at least one special character')

    return errors


@require_POST
def register(request: HttpRequest) -> JsonResponse:
    try:
        payload = loads(request.body.decode('utf-8') or '{}')
    except JSONDecodeError:
        return JsonResponse({'detail': 'Invalid JSON'}, status=400)

    username = (payload.get('username') or '').strip()
    full_name = (payload.get('full_name') or '').strip()
    email = (payload.get('email') or '').strip()
    password = payload.get('password')

    errors: dict[str, list[str]] = {}

    if not username:
        errors.setdefault('username', []).append('Username is required')
    elif not USERNAME_RE.match(username):
        errors.setdefault('username', []).append(
            'Username must be 4-20 chars, latin letters/digits, first char is a letter'
        )
    elif User.objects.filter(username=username).exists():
        errors.setdefault('username', []).append('Username already exists')

    if not full_name:
        errors.setdefault('full_name', []).append('Full name is required')

    if not email:
        errors.setdefault('email', []).append('Email is required')
    elif not EMAIL_RE.match(email):
        errors.setdefault('email', []).append('Invalid email format')

    pw_errors = validate_password(password)
    if pw_errors:
        errors['password'] = pw_errors

    if errors:
        return JsonResponse({'detail': 'Validation error', 'errors': errors}, status=400)

    storage_rel_path = f'{username}_{uuid4()}/'

    user = User(
        username=username,
        full_name=full_name,
        email=email,
        storage_rel_path=storage_rel_path,
        is_admin=False,
    )

    user.set_password(password)
    user.save()
    ensure_user_storage_dir(user.storage_rel_path)

    return JsonResponse(
        {
            'id': user.id,
            'username': user.username,
            'full_name': user.full_name,
            'email': user.email,
            'is_admin': user.is_admin,
            'storage_rel_path': user.storage_rel_path,
        },
        status=201,
    )

@require_POST
def login_view(request: HttpRequest) -> JsonResponse:
    try:
        payload = loads(request.body.decode('utf-8') or '{}')
    except JSONDecodeError:
        return JsonResponse({'detail': 'Invalid JSON'}, status=400)

    username = (payload.get('username') or '').strip()
    password = payload.get('password') or ''

    if not username or not password:
        return JsonResponse({'detail': 'Missing username or password'}, status=400)

    user = authenticate(request, username=username, password=password)
    if user is None:
        return JsonResponse({'detail': 'Invalid credentials'}, status=401)

    login(request, user)

    return JsonResponse(
        {
            'detail': 'Login successful',
            'user': {
                'id': user.id,
                'username': user.username,
                'full_name': user.full_name,
                'email': user.email,
                'is_admin': user.is_admin,
                'is_superuser': user.is_superuser,
                'is_staff': user.is_staff,
            },
        },
        status=200,
    )

@require_GET
def logout_view(request: HttpRequest) -> JsonResponse:
    if not request.user.is_authenticated:
        return JsonResponse({'detail': 'Not authenticated'}, status=401)

    logout(request)

    return JsonResponse({'detail': 'Logout successful'}, status=200)

@require_GET
def admin_users_list(request: HttpRequest) -> JsonResponse:
    if not request.user.is_authenticated:
        return JsonResponse({'detail': 'Authentication required'}, status=401)

    actor_level = get_user_level(request.user)
    if actor_level == 'user':
        return JsonResponse({'detail': 'Admin rights required'}, status=403)

    qs = User.objects.all().order_by('id')

    actor = request.user
    actor_id = request.user.id

    data = [
        {
            'id': u.id,
            'username': u.username,
            'full_name': u.full_name,
            'email': u.email,

            'is_admin': u.is_admin,
            'is_staff': u.is_staff,
            'is_superuser': u.is_superuser,

            'level': get_user_level(u),
            'rank': get_user_rank(u),

            'storage_rel_path': u.storage_rel_path,
        }
        for u in qs if u.id == actor_id or can_manage_user(actor, u)
    ]

    return JsonResponse(data, safe=False)

@require_http_methods(['DELETE'])
def admin_user_delete(request: HttpRequest, user_id: int) -> JsonResponse:
    if not request.user.is_authenticated:
        return JsonResponse({'detail': 'Authentication required'}, status=401)

    actor_level = get_user_level(request.user)
    if actor_level == 'user':
        return JsonResponse({'detail': 'Admin rights required'}, status=403)

    target = User.objects.filter(id=user_id).first()
    if not target:
        return JsonResponse({'detail': 'User not found'}, status=404)

    if not can_delete_user(request.user, target):
        return JsonResponse({'detail': 'Forbidden'}, status=403)

    if target.is_superuser:
        superusers_count = User.objects.filter(is_superuser=True).count()
        if superusers_count < 2:
            return JsonResponse(
                {'detail': 'Can\'t delete the last superuser'},
                status=409
            )

    delete_files = request.GET.get('delete_files') == '1'

    if delete_files:
        try:
            root = user_storage_abs_path(target.storage_rel_path)
            if root.exists():
                for p in sorted(root.rglob('*'), reverse=True):
                    if p.is_file():
                        p.unlink()
                    else:
                        p.rmdir()
                root.rmdir()
        except Exception:
            return JsonResponse(
                {'detail': 'Failed to delete user files'},
                status=500
            )

    target.delete()

    return JsonResponse(
        {
            'detail': 'User deleted',
            'files_deleted': delete_files
        },
        status=200,
    )

@require_http_methods(['PATCH'])
def admin_user_set_level(request: HttpRequest, user_id: int) -> JsonResponse:
    if not request.user.is_authenticated:
        return JsonResponse({'detail': 'Authentication required'}, status=401)

    actor = request.user
    actor_level = get_user_level(actor)

    if actor_level == 'user':
        return JsonResponse({'detail': 'Admin rights required'}, status=403)

    try:
        target = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({'detail': 'User not found'}, status=404)

    try:
        payload = loads(request.body.decode('utf-8') or '{}')
    except JSONDecodeError:
        return JsonResponse({'detail': 'Invalid JSON'}, status=400)

    new_level = payload.get('level')

    if not new_level:
        return JsonResponse({'detail': 'Missing level'}, status=400)

    if new_level not in ('user', 'admin', 'senior_admin', 'superuser'):
        return JsonResponse({'detail': 'Invalid level'}, status=400)

    if not can_change_level(actor, target, new_level):
        return JsonResponse({'detail': 'Permission denied'}, status=403)

    if target.is_superuser and new_level != 'superuser':
        superusers_count = User.objects.filter(is_superuser=True).count()
        if superusers_count < 2:
            return JsonResponse(
                {'detail': 'Can\'t remove last superuser'},
                status=400
            )

    set_user_level(target, new_level)

    return JsonResponse(
        {
            'detail': 'User level updated',
            'user': {
                'id': target.id,
                'username': target.username,
                'level': get_user_level(target),
                'is_admin': target.is_admin,
                'is_staff': target.is_staff,
                'is_superuser': target.is_superuser,
            },
        },
        status=200,
    )
