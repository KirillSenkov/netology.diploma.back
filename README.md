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
Файлы загружаются в папку `storage_data/` по .env.  
Каждому пользователю автоматически создаётся собственная директория (на основе `username + UUID`).

## API
Проверятся активная сессия.  
Для POST/PATCH/DELETE требуется CSRF-токен
(cookie csrftoken, заголовок X-CSRFToken).  
Получение cookie: GET `/api/auth/csrf/`
### Загрузка файла
POST `/api/files/upload/`  
Формат: `multipart/form-data`
Поля:
- `file` — файл
- `comment` — строка (опционально)

Ответ: JSON с информацией о файле.
### Получение списка файлов
Администратор может получить список файлов
любого пользователя через параметр user_id.
GET `/api/files/[?<user_id>]`  
Ответ: JSON-массив файлов пользователя.
### Удаление файла
DELETE `/api/files/<id>/`  
Файл удаляется:
- из файлового хранилища
- из базы данных

Ответ: JSON { detail: "File deleted" }.
### Переименование файла
PATCH `/api/files/<id>/rename/`  
Формат: `application/json`  
Ответ: JSON { id: 3, original_name: "new_name.txt" }
### Скачивание файла (по авторизации)
GET `/api/files/<id>/download/`  
Обычный пользователь может скачивать только свои файлы.  
Администратор — любые.
### Спецссылка на файл
Включить:
POST `/api/files/<id>/share/`  
Т.к. это действие по смыслу, а не просто UPDSTE  
Выключить:
POST `/api/files/<id>/share/disable/`  
Т.к. это действие по смыслу, а не просто UPDSTE  
Скачать по спецссылке:  
Активная сессия НЕ проверяется.  
GET `/share/<uuid>/`
### Изменение комментария файла
PATCH `/api/files/<id>/comment/`  
Формат: `application/json`  
Ответ: JSON { "comment": "New comment" }  
Для удаления комментария:
{ "comment": null } | { "comment": "" }

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
- [x] Download with auth API
- [x] File comment API
- [x] Storage REST API
- [ ] Users/Auth REST API
