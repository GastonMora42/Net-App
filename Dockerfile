FROM python:3.10

WORKDIR /app

COPY api/requirements.txt .

COPY [".", "/app"]

RUN pip install -U pip && pip install -r requirements.txt

RUN pip install --no-cache-dir gunicorn

COPY api/ ./api

COPY initializer.sh .

RUN chmod +x initializer.sh

EXPOSE 8000

ENTRYPOINT  ["./initializer.sh"]