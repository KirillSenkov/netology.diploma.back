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
6. Файлы загружаются в папку `storage_data/` по .env.

## Чеклист
- [x] Проект Django
- [x] PostgreSQL подключение и БД
- [x] apps: users, storage
- [x] AbstractUser
- [x] Хранилище для File настроено (STORAGE_ROOT)
- [ ] REST API
