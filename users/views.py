from json import loads, JSONDecodeError
from re import compile as make_regex
from uuid import uuid4

from django.contrib.auth import authenticate, login
from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import (
    require_GET,
    require_POST,
    require_http_methods
)
from django.views.decorators.csrf import ensure_csrf_cookie

from .models import User
from storage.services import ensure_user_storage_dir

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
