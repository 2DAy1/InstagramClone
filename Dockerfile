# Dockerfile
FROM python:3.12-slim

# Використовуємо bash та робочу папку /app
SHELL ["/bin/bash", "-c"]
WORKDIR /app

# Не генерувати .pyc, не буферизувати вивід
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Копіюємо залежності й ставимо їх
COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# Копіюємо решту коду
COPY . .

# Збираємо статику (опціонально, якщо у тебе collectstatic)
# RUN python manage.py collectstatic --noinput

# Відкриваємо порт 8000
EXPOSE 8000

# Запускаємо Gunicorn з нашим WSGI-модулем
CMD ["gunicorn", "src.wsgi:application", "--bind", "0.0.0.0:8000"]
