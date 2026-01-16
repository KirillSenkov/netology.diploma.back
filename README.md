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
Каждому пользователю автоматически создаётся собственная директория (на основе `username + UUID`).

## API
### Загрузка файла
POST `/api/files/upload/`

Формат: `multipart/form-data`
Поля:
- `file` — файл
- `comment` — строка (опционально)

Проверятся активная сессия.

Ответ: JSON с информацией о файле.

## Чеклист
- [x] Проект Django
- [x] PostgreSQL подключение и БД
- [x] apps: users, storage
- [x] AbstractUser
- [x] Хранилище для File настроено (STORAGE_ROOT)
- [x] File upload API
- [ ] File list API
- [ ] Delete / rename / share
- [ ] REST API
