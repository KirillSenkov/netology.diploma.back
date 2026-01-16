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
Проверятся активная сессия.<br>
Для POST/PATCH/DELETE требуется CSRF-токен
(cookie csrftoken, заголовок X-CSRFToken).<br>
Получение cookie: GET `/api/auth/csrf/`
### Загрузка файла
POST `/api/files/upload/`<br>
Формат: `multipart/form-data`
Поля:
- `file` — файл
- `comment` — строка (опционально)

Ответ: JSON с информацией о файле.
### Получение списка файлов
GET `/api/files/`<br>
Ответ: JSON-массив файлов пользователя.
### Удаление файла
DELETE `/api/files/<id>/`<br>
Файл удаляется:
- из файлового хранилища
- из базы данных

Ответ: JSON { detail: "File deleted" }.
### Переименование файла
PATCH `/api/files/<id>/rename/`<br>
Формат: `application/json`<br>
Ответ: JSON { id: 3, original_name: "new_name.txt" }
### Скачивание файла (по авторизации)
GET `/api/files/<id>/download/`<br>
Обычный пользователь может скачивать только свои файлы.<br>
Администратор — любые.
### Спецссылка на файл
Включить:
POST `/api/files/<id>/share/`<br>
Т.к. это действие по смыслу, а не просто UPDSTE<br>
Выключить:
POST `/api/files/<id>/share/disable/`<br>
Т.к. это действие по смыслу, а не просто UPDSTE<br>
Скачать по спецссылке:<br>
Активная сессия НЕ проверяется.<br>
GET `/share/<uuid>/`

## Чеклист
- [x] Django project
- [x] PostgreSQL DB connection
- [x] apps: users, storage
- [x] AbstractUser
- [x] Storage of File's set (STORAGE_ROOT)
- [x] File upload API
- [x] File list API
- [x] File delete API
- [x] Add CSRF-auth
- [x] File rename API 
- [x] Share link API
- [ ] Download with auth API 
- [ ] REST API
