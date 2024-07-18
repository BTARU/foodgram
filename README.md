Хост: http://51.250.30.149/
Админка:

#  Проект Foodgram

## Описание

Foodgram это сайт, на котором пользователи могут публиковать свои рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов.
Зарегистрированным пользователям также доступен сервис «Список покупок». Он позволяет создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

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

## Технологии

Backend: Django Rest Framework, запущенный на web-сервере Gunicorn.

Frontend: React.

База Данных: PostgreSQL.

Связь между браузером пользователя и сервером настроена через Web-сервер Nginx.

## Автор

[Bulat Ayupov](https://github.com/BTARU)