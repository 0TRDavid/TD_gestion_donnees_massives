FROM python:3.12-slim

WORKDIR /dbt
ENV PYTHONUNBUFFERED=1 DBT_PROFILES_DIR=/dbt
RUN pip install --no-cache-dir "dbt-core==1.9.0" "dbt-postgres==1.9.0"
COPY . .

CMD ["dbt", "build"]
