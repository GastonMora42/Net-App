FROM python:3.11

WORKDIR /app

COPY api/requirements.txt .

COPY [".", "/app"]

ENV PIP_TIMEOUT=2000

RUN pip install -U pip && pip install -r requirements.txt

RUN pip install --no-cache-dir gunicorn

COPY api/ ./api

COPY initializer.sh .

RUN chmod +x initializer.sh

ENV PORT=8080

EXPOSE 8080

ENTRYPOINT  ["./initializer.sh"]