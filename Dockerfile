FROM python:3.11-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y build-essential

# Устанавливаем переменные
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Создаем директорию
WORKDIR /app

# Устанавливаем зависимости
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Копируем проект полностью (включая db.sqlite3)
COPY . .

# Открываем порт и запускаем
EXPOSE 8000
CMD ["gunicorn", "schramberg.wsgi:application", "--bind", "0.0.0.0:8000"]
