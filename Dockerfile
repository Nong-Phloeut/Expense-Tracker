# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Collect static files (optional)
RUN python manage.py collectstatic --noinput

EXPOSE 8080

CMD ["gunicorn", "expense_tracker.wsgi:application", "--bind", "0.0.0.0:8080"]
