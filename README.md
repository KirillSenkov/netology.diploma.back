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

### CSRF cookie
GET `/api/auth/csrf/`  
Печёт cookie `csrftoken` для POST/PATCH/DELETE.

### Загрузка файла
POST `/api/files/upload/`  
Формат: `multipart/form-data`  
Поля:
- `file` — файл
- `comment` — строка (опционально)
Ответ: JSON с информацией о файле.

### Получение списка файлов
Доступ к чужим файлам через параметр user_id зависит от уровня:
 - `admin → файлы user`
 - `senior_admin → файлы user и admin`
 - `superuser → любые файлы`
GET `/api/files/[?<user_id>]`  
Ответ: JSON-массив файлов пользователя.

### Удаление файла
Доступ к чужим файлам аналогично получению списка.  
DELETE `/api/files/<id>/`  
Файл удаляется:
- из файлового хранилища
- из базы данных
Ответ: JSON { detail: "File deleted" }.

### Переименование файла
Доступ к чужим файлам аналогично получению списка.  
PATCH `/api/files/<id>/rename/`  
Формат: `application/json`  
Ответ: JSON { id: 3, original_name: "new_name.txt" }

### Скачивание файла (по авторизации)
GET `/api/files/<id>/download/`  
Доступ к чужим файлам аналогично получению списка.  

### Спецссылка на файл
Включить:  
Доступ к чужим файлам аналогично получению списка.  
POST `/api/files/<id>/share/`  
Т.к. это действие по смыслу, а не просто UPDSTE  
Выключить:  
Доступ к чужим файлам аналогично получению списка.  
POST `/api/files/<id>/share/disable/`  
Т.к. это действие по смыслу, а не просто UPDSTE  
Скачать по спецссылке:  
Активная сессия НЕ проверяется.  
GET `/share/<uuid>/`

### Изменение комментария файла
Доступ к чужим файлам аналогично получению списка.  
PATCH `/api/files/<id>/comment/`  
Формат: `application/json`  
Ответ: JSON { "comment": "New comment" }  
Для удаления комментария:
{ "comment": null } | { "comment": "" }

### Регистрация нового пользователя
POST `/api/auth/register/`  
Формат: `application/json`  
Поля:
- `username` — строка (4..20, латиница/цифры, первый символ — буква)
- `full_name` — строка
- `email` — строка (формат email, не уникален)
- `password` — строка (>=6, 1 заглавная, 1 цифра, 1 спецсимвол)
При регистрации автоматически генерируется относительный путь для папки 
пользователя и она создается в хранилище на диске.  
Ответ: JSON с данными пользователя.  
Ошибки: 400 JSON с `errors` с раскладкой по полям.

### Вход
POST `/api/auth/login/`  
Создаёт серверную сессию пользователя.  
Тело запроса: `{ "username": "user0001", "password": "Pass#1"
 }`  
Ответ: 
`{
  "detail": "Login successful",
  "user": {
    "id": 2,
    "username": "user0001",
    "full_name": "Test User",
    "email": "u@m.l",
    "is_admin": false,
    "is_superuser": false,
    "is_staff": false,
    "level": "user",
    "rank": 3
  }
}`

### Выход
GET `/api/auth/logout/`  
Завершает текущую сессию.  
Ответ: `{ "detail": "Logout successful" }`

## Админ API
Проверятся активная сессия.  
Для POST/PATCH/DELETE требуется CSRF-токен
(cookie csrftoken, заголовок X-CSRFToken).  

### CSRF cookie
GET `/api/auth/csrf/`  
Печёт cookie `csrftoken` для POST/PATCH/DELETE.

### Список пользователей
GET `/api/admin/users/`  
Доступ:
- `admin → видит user (+ себя)`
- `senior_admin → видит user + admin (+ себя)`
- `superuser → видит всех`
Ответ: JSON-массив пользователей, включает `level` и `rank`.

### Удалить пользователя
DELETE `/api/admin/users/<id>/`  
Доступ по иерархии ролей (user → 403).  
Опционально: удалить файлы и папку пользователя — `?delete_files=1`  
Ответ: JSON `{ detail: "User deleted", files_deleted: true|false }`
Запрет на удаление последнего superuser.

### Управление ролями пользователей
PATCH `/api/admin/users/<id>/level/`  
Формат: `application/json`  
Тело запроса:
{ "level": "user" | "admin" | "senior_admin" | "superuser" }  
Права:
- senior_admin → user, admin  
- superuser → все
Поднимать до / опускать со своего уровня имеет право только superuser.  
Запрет на изменение роли последнего superuser.

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
- [x] User registration API with validation
- [x] Users/Auth REST API
- [x] Add admin users list API
- [X] Admin users level API
- [x] Admin users delete API
- [x] Admin Users Management API
- [x] Users/Auth logout API
