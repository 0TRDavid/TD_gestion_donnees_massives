FROM python:3.12-slim

WORKDIR /dbt
ENV PYTHONUNBUFFERED=1 DBT_PROFILES_DIR=/dbt
RUN pip install --no-cache-dir "dbt-core==1.9.0" "dbt-postgres==1.9.0"
COPY . .

EXPOSE 8080
# build (modèles + tests), puis génération et mise à disposition de la documentation
CMD ["sh", "-c", "dbt build && dbt docs generate && dbt docs serve --host 0.0.0.0 --port 8080 --no-browser"]
