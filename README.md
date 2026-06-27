# API YaMDb

YaMDb собирает отзывы пользователей на произведения (фильмы, книги, музыка
и т.д.). Произведения делятся на категории и жанры. Пользователи оставляют
отзывы с оценкой и комментарии к ним, а средняя оценка формирует рейтинг
произведения.

## Авторы

- Иван Кононенко — [@Zloyslon1](https://github.com/Zloyslon1)
- Александр Крылов — [@mraksdev](https://github.com/mraksdev)
- Степан Пименов — [@Stepan-Pimenov](https://github.com/Stepan-Pimenov)

## Технологии

- Python 3.12
- Django 5.1
- Django REST Framework 3.15
- Simple JWT
- django-filter

## Развёртывание

```bash
git clone git@github.com:Zloyslon1/api-yamdb.git
cd api-yamdb

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp api_yamdb/.env.example api_yamdb/.env

cd api_yamdb
python manage.py migrate
```

В Windows виртуальное окружение активируется командой
`venv\Scripts\activate`. После копирования `.env` нужно вписать в него
свой `SECRET_KEY`.

## Загрузка тестовых данных из CSV

Из каталога `api_yamdb` одной командой:

```bash
python manage.py load_csv
```

## Запуск

```bash
cd api_yamdb
python manage.py runserver
```

## Документация API

Полная документация (redoc) доступна после запуска сервера по адресу:
http://127.0.0.1:8000/redoc/

## Примеры запросов

- Регистрация: `POST /api/v1/auth/signup/` — `{"email": "...", "username": "..."}`
- Получение токена: `POST /api/v1/auth/token/` — `{"username": "...", "confirmation_code": "..."}`
- Список произведений: `GET /api/v1/titles/`
- Отзывы на произведение: `GET /api/v1/titles/{title_id}/reviews/`
- Комментарии к отзыву: `GET /api/v1/titles/{title_id}/reviews/{review_id}/comments/`
