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
4. Создать и рименить миграции:
   - `python manage.py makemigrations`
   - `python manage.py migrate`
5. Запуск сервера:
   - `python manage.py runserver`

## Хранилище
Файлы загружаются в папку `storage_data/` по .env.<br>
Каждому пользователю автоматически создаётся собственная директория (на основе `username + UUID`).

## API
### Загрузка файла
POST `/api/files/upload/`<br>
Формат: `multipart/form-data`
Поля:
- `file` — файл
- `comment` — строка (опционально)

Проверятся активная сессия.<br>
Ответ: JSON с информацией о файле.
### Получение списка файлов
GET `/api/files/`<br>
Проверятся активная сессия.<br>
Ответ: JSON-массив файлов пользователя.
### Удаление файла
DELETE `/api/files/<id>/`<br>
Проверятся активная сессия.<br>
Файл удаляется:
- из файлового хранилища
- из базы данных

Ответ: JSON { detail: "File deleted" }.

## Чеклист
- [x] Проект Django
- [x] PostgreSQL подключение и БД
- [x] apps: users, storage
- [x] AbstractUser
- [x] Хранилище для File настроено (STORAGE_ROOT)
- [x] File upload API
- [x] File list API
- [x] File delete API
- [ ] Rename / share
- [ ] REST API
