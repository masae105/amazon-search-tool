FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD exec gunicorn --bind :${PORT:-8080} --workers 1 --threads 8 --timeout 0 app:appFROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD exec gunicorn --bind :${PORT:-8080} --workers 1 --threads 8 --timeout 0 app:app