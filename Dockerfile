FROM python:3.11-alpine

# Устанавливаем системные зависимости
RUN apk add --no-cache \
    gcc \
    musl-dev \
    linux-headers \
    postgresql-dev \
    libffi-dev

WORKDIR /app

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копируем приложение
COPY app/ .

# Создаем пользователя для безопасности
RUN adduser -D myuser && chown -R myuser:myuser /app
USER myuser

EXPOSE 5000

CMD ["python", "app.py"]
