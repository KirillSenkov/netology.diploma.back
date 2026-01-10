# My Cloud — Backend (Django + PostgreSQL)

## Требования
- Python 3.10+
- PostgreSQL
- DBeaver (опционально)

## Установка и запуск (dev)
1. Создать БД PostgreSQL: `my_cloud`
2. Настроить подключение в `config/settings.py` (DATABASES)
3. Устанвить зависимости:
   - `pip install django psycopg[binary]`
4. Применить миграции:
   - `python manage.py migrate`
5. Запуск сервера:
   - `python manage.py runserver`

## Чеклист
- [x] Проект Django
- [x] PostgreSQL подключение и БД
- [x] apps: users, storage
- [ ] AbstractUser
- [ ] REST API
