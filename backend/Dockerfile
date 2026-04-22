FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV BACKEND_PORT=3000
ENV DATA_FILES=/app/data/provider-alpha.json,/app/data/provider-beta.json,/app/data/provider-gamma.json

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY app.py /app/app.py
COPY normalize_data.py /app/normalize_data.py
COPY data/ /app/data/

EXPOSE 3000

CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${BACKEND_PORT}"]