# Dockerfile for the Flask API
FROM python:3.12-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

ENV FLASK_ENV=production
ENV PORT=5000
ENV HOST=0.0.0.0

CMD ["python", "serve.py"]

