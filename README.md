# Wallet API

Тестовое задание для компании "Академия IT".

---

## Описание

С помощью данного приложения пользователь может управлять своим виртуальный кошельком и следить за его состоянием.

Приложение обеспечивает следующую функциональность и особенности:
- Регистрация пользователя с помощью кастомного эндпоинта и аутентификация с помощью пары JWT-токенов.
- Обновление access-токена и принудительное добавление refresh-токена в Blacklist.
- Создание, удаление и вывод информации о кошельке. Вывод списка всех кошельков пользователя.
- Получения списка всех операций над кошельком.
- Возможность пополнения и снятия денежных средств. Защита от параллельных операций.
- Привязка кошельков к пользователям.
- Дополнительная валидация на уровне моделей.
- Автоматическая Swagger-документация API с помощью drf-yasg.
- Покрытие тестами всех эндпоинтов проекта.
- Код соответствует стандарту PEP8.
- Переменные окружения выведены в отдельный файл. Для работы с ними используется библиотека dotenv.
- Для чистоты кода были использованы black, isort и flake8.
- Настроена Admin-панель.
- Запуск приложения в контейнере через docker-compose.

---

## Технологический стек
* Язык: Python 3.8+.
* Веб-фреймворк: Django 5+ (с использованием встроенной ORM и REST Framework).
* База данных: PostgreSQL (по умолчанию).
* Развёртывание: Docker + docker-compose.

---

## Установка и настройка
0) Предварительно необходимо настроить переменные окруженния.

1) Клонируем репозиторий:
```bash
git clone https://github.com/MLKolt/Wallets-API.git
```
2) Переходим в папку проекта и копируем туда свой .env файл (по умолчанию используется файл-пример .env_example).

3) Запускаем проект:
```bash
docker-compose --env-file <.название_env_файла> up --build
```

4) Создаём суперпользователя:
```bash
docker-compose exec web python manage.py createsuperuser
```

5) Тесты:
```bash
docker-compose exec web python manage.py test wallets
```

## Работа с приложением

1) Автоматическая документация:
```bash
#Swagger-UI:  
http://127.0.0.1:8000/swagger/
# ReDoc:  
http://127.0.0.1:8000/redoc/
```

2) Регистрация (POST):
```bash
http://127.0.0.1:8000/api/v1/register/
```
```bash
{
  "username": "<user_name>",
  "password": "<password>"
}
```

3) Получение пары токенов (POST):
```bash
http://127.0.0.1:8000/api/v1/token/
```
```bash
{
  "username": "<user_name>",
  "password": "<password>"
}
```

4) Обновление access-токена (POST):
```bash
http://127.0.0.1:8000/api/v1/token/refresh/
```
```bash
{
  "refresh": "<refresh_токен>"
}
```

5) Blacklist для актуального refresh-токена (POST):
```bash
http://127.0.0.1:8000/api/v1/logout/
```
```bash
{
  "refresh": "<refresh_токен>"
}
```

6) Создание кошелька (POST):
```bash
http://127.0.0.1:8000/api/v1/wallet/
```
```bash
Authorization: Bearer <ваш_access_токен>
```

7) Детальная информаци о кошельке (GET):
```bash
http://127.0.0.1:8000/api/v1/wallets/<wallet_id>/
```
```bash
Authorization: Bearer <ваш_access_токен>
```

8) Список всех кошельков пользователя (GET):
```bash
http://127.0.0.1:8000/api/v1/wallets/all/
```
```bash
Authorization: Bearer <ваш_access_токен>
```

9) Удаление кошелька (DELETE):
```bash
http://127.0.0.1:8000/api/v1/wallets/<wallet_id>/
```
```bash
Authorization: Bearer <access_токен>
```

9) Пополнение / Снятие с кошелька (POST):
```bash
http://127.0.0.1:8000/api/v1/wallets/<wallet_id>/operation/
```
```bash
Authorization: Bearer <ваш_access_токен>
```
```bash
{
    "type": "<DEPOSIT / WITHDRAW>",
    "amount": <сумма>
}
```

10) Все операции над кошельком (GET):
```bash
http://127.0.0.1:8000/api/v1/wallets/<wallet_id>/operations/
```
```bash
Authorization: Bearer <ваш_access_токен>
```