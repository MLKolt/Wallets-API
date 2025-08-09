#!/bin/sh

# Останавить выполнение при любой ошибке
set -e

# Ожидание готовности БД
echo "Ожидание готовности БД..."
while ! nc -z db 5432; do
  sleep 1
done

echo "База данных готова!"

# Применить миграции Django
python manage.py migrate --noinput

# Запустить сервер
exec "$@"