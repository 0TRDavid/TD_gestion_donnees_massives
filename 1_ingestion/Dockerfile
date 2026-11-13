FROM python:3.13-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1 PYTHONUTF8=1
RUN pip install --no-cache-dir "psycopg[binary]==3.2.3"
COPY . .
CMD ["sh", "-c", "python ingestion.py && python charger_raw.py"]