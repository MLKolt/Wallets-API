# Лёгкая версия Python
FROM python:3.12-slim

# Стандартная установка системных пакетов
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl netcat-openbsd && rm -rf /var/lib/apt/lists/*

# Без .pyc
# Вывод python сразу в консоль, без буфера
# Без pip кэша
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Задать рабочую папку
WORKDIR /docker_wallet

# Установить зависимости
COPY requirements.txt .
RUN pip install -r requirements.txt

# Копировать проект в рабочую папку
COPY . .

# Стартовый скрипт
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Открыть порт и установить точку входа
EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]