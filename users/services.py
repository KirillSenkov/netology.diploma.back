from .models import User

def level_to_rank(level_name: str) -> int:
    levels = {
        'user': 3,
        'admin': 2,
        'senior_admin': 1,
        'superuser': 0,
    }

    if level_name not in levels:
        raise ValueError(f'Unknown level: {level_name}')

    return levels[level_name]

def rank_to_level(level_rank: int) -> str:
    ranks = {
        3: 'user',
        2: 'admin',
        1: 'senior_admin',
        0: 'superuser',
    }

    return ranks[level_rank]

def get_user_level(user: User) -> str:
    if user.is_superuser:
        return 'superuser'
    if user.is_admin and user.is_staff:
        return 'senior_admin'
    if user.is_admin:
        return 'admin'
    return 'user'

def get_user_rank(user: User) -> int:
    if user.is_superuser:
        return 0
    if user.is_admin and user.is_staff:
        return 1
    if user.is_admin:
        return 2
    return 3

def set_user_level(user: User, level: str):
    if level == 'user':
        user.is_admin = False
        user.is_staff = False
        user.is_superuser = False

    elif level == 'admin':
        user.is_admin = True
        user.is_staff = False
        user.is_superuser = False

    elif level == 'senior_admin':
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = False

    elif level == 'superuser':
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True

    else:
        raise ValueError('Unknown level')

    user.save(update_fields=['is_admin', 'is_staff', 'is_superuser'])

def can_manage_user(actor: User, target: User) -> bool:
    actor_rank = get_user_rank(actor)
    target_rank = get_user_rank(target)

    if actor_rank == 0:
        return True

    return actor_rank < target_rank

def can_delete_user(actor: User, target: User) -> bool:
    return can_manage_user(actor, target)

def can_manage_files(actor: User, file_owner: User) -> bool:
    if actor == file_owner:
        return True

    return can_manage_user(actor, file_owner)

def can_change_level(actor: User, target: User, new_level: str) -> bool:
    actor_rank = get_user_rank(actor)
    target_rank = get_user_rank(target)
    new_rank = level_to_rank(new_level)

    if actor_rank == 0 and target_rank != new_rank:
        return True

    if actor_rank == 1: # сеньёр
        return min(target_rank, new_rank) > 1 and target_rank != new_rank

    return False
