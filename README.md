#  Проект Foodgram

## Описание

Foodgram это сайт, на котором пользователи могут публиковать свои рецепты, добавлять чужие рецепты в избранное и
подписываться на публикации других авторов.
Зарегистрированным пользователям также доступен сервис «Список покупок». Он позволяет создавать список продуктов,
которые нужно купить для приготовления выбранных блюд.

## Запуск проекта

#### Клонировать репозиторий и перейти в него в командной строке:

```
https://github.com/BTARU/foodgram.git
```

### Как запустить проект(продакшен):

#### База Данных

Для продакшен версии предполагается подключение БД PostgreSQL. Для этого нужно добавить переменную окружения DB_POSTGRES = True в файл .env в корне проекта и остальные переменные для Postgres согласно переменной DATABASES в settings.py.

Проект запускается в трех контейнерах Docker, связанных между собой Docker Network.

Для запуска проекта на сервере Ubuntu в контейнерах docker:
1) Создайте папку foodgram и переместите в нее файл docker-compose.production.yml
2) В папке foodgram выполните команды в терминале:

```
sudo docker compose -f docker-compose.production.yml pull
```

```
sudo docker compose -f docker-compose.production.yml down
```

```
sudo docker compose -f docker-compose.production.yml up -d
```

Сбор статики и выполнений миграций БД.

```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
```

```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
```

```
sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/
```

Также на сервере должен быть запущен прокси сервер для переадресации с порта, выбранного в backend части проекта.

### Как запустить только backend часть проекта локально:

Нужно изменить БД с Postgres на SQLite. Для этого удалите переменную DB_POSTGRES в файле окружения .env

Выполняем команды в терминале:

```
cd backend
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

* Если у вас Linux/macOS

    ```
    source env/bin/activate
    ```

* Если у вас windows

    ```
    source env/scripts/activate
    ```

```
python3 -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```

## Реализованные API:
Примеры запросов:

```
POST /api/users/ - Регистрация нового пользователя
POST /api/auth/token/login/ - Получение токена для пользователя
POST /api/users/set_password/ - Изменение пароля

GET /api/users/ - Получение списка всех пользователей
GET /api/users/{user_id} - Получение профиля пользователя

GET /api/users/subscriptions/ - Возвращает пользователей, на которых подписан текущий пользователь.
POST /api/users/{user_id}/subscribe/ - Подписаться на пользователя
DELETE /api/users/{user_id}/subscribe/ - Отписаться от пользователя

GET /api/tags/ - Получение списка всех тэгов

GET /api/ingredients/ - Получение списка всех ингредиентов

GET /api/recipes/ - Получение списка всех рецептов
POST /api/recipes/ - Создание рецепта пользователем
GET /api/recipes/{recipe_id} - Получение рецепта
PATCH /api/recipes/{recipe_id} - Обновление  рецепта его автором
DELETE /api/recipes/{recipe_id} - Удаление  рецепта его автором
GET /api/recipes/{recipe_id}/get-link/ - Получить короткую ссылку на рецепт

POST /api/recipes/{id}/favorite/ - Добавить рецепт в избранное
DELETE /api/recipes/{id}/favorite/ - Удалить рецепт из избранного

GET /api/recipes/download_shopping_cart/ - Скачать файл со списком покупок. Формат CSV.
POST /api/recipes/{id}/shopping_cart/ - Добавить рецепт в список покупок
DELETE /api/recipes/{id}/shopping_cart/ - Удалить рецепт из списка покупок
```

### Полная спецификация API:

Посмотреть полную спецификацию API можно по адресу: <домен>/api/docs/

## Технологии

Backend: Django Rest Framework, запущенный на web-сервере Gunicorn.

Frontend: React.

База Данных: PostgreSQL.

Связь между браузером пользователя и сервером настроена через Web-сервер Nginx.

## Автор

[Bulat Ayupov](https://github.com/BTARU)
