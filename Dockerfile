FROM python:3.12-slim

WORKDIR /app

ENV DATABASE_URL=postgresql://biblio_user:biblio_pass@db:5432/biblio

# Dépendances système pour psycopg2
RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq-dev gcc postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

# wait-for-db helper
COPY scripts/wait-for-db.sh /usr/local/bin/wait-for-db.sh
RUN chmod +x /usr/local/bin/wait-for-db.sh

EXPOSE 8001

CMD ["sh", "-c", "/usr/local/bin/wait-for-db.sh && uvicorn app.api:app --host 0.0.0.0 --port 8001"]
