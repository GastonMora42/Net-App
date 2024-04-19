FROM python:3.11

WORKDIR /app

COPY api/requirements.txt .

COPY [".", "/app"]


COPY --from=secret-volume /secret /projects/711857199805/secrets/OPENAI_API_KEY/versions/1
# Configura el secreto como una variable de entorno
RUN export OPENAI_API_KEY=$(echo $OPENAI_API_KEY)

ENV PIP_TIMEOUT=2000

RUN pip install -U pip && pip install -r requirements.txt

RUN pip install --no-cache-dir gunicorn

COPY api/ ./api

COPY initializer.sh .

RUN chmod +x initializer.sh

ENV PORT=8080

EXPOSE 8080

ENTRYPOINT  ["./initializer.sh"]