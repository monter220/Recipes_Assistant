# Продуктовый помощник

## Описание проекта

сайт доступен по адресу foodpractishelp.ddns.net

Приложение «Продуктовый помощник»: сайт, на котором пользователи будут публиковать рецепты, добавлять чужие рецепты 
в избранное и подписываться на публикации других авторов. Сервис «Список покупок» позволит пользователям создавать 
список продуктов, которые нужно купить для приготовления выбранных блюд.


## Технологии

* Python
* Django
* Django REST Framework
* Postgres
* Docker
* Djoser


## Установка

1. Склонировать репозиторий

```commandline
git clone git@github.com:monter220/foodgram-project-react.git
```

2. В директории infra переименовать файл `env.example -> .env` и изменить переменные окружения в соответсвии с Вашими условиями.
3. Для работы с проектом необходимо установить `Docker` и `Docker-compose` и выполнить команды для сборки контейнеров:
```
cd infra
docker compose up -d --build
```
4. Внутри контейнера необходимо выполнить миграции и собрать статику приложения, по необходимости создать суперюзера:

```
docker compose exec backend python manage.py makemigrations
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py collectastatic
docker compose exec backend python manage.py load_ingredients_from_csv
docker compose exec backend python manage.py createsuperuser
```

## Admin_zone

Админка доступна по паре логин/пароль - `q@q.ru/Cbv0yegfktc`
