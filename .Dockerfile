FROM python:3.9-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

CMD ["gunicorn", "api:app", "--bind", "0.0.0.0:8080"]