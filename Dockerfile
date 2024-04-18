FROM python:3.11

WORKDIR /app

COPY api/requirements.txt .

COPY [".", "/app"]

# Instala el SDK de Google Cloud
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    lsb-release

RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
RUN curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -
RUN apt-get update -y && apt-get install google-cloud-sdk -y

# Configura el secreto como una variable de entorno
RUN export OPENAI_API_KEY=$(gcloud secrets versions access latest --secret="OPENAI_API_KEY")

ENV PIP_TIMEOUT=2000

RUN pip install -U pip && pip install -r requirements.txt

RUN pip install --no-cache-dir gunicorn

COPY api/ ./api

COPY initializer.sh .

RUN chmod +x initializer.sh

ENV PORT=8080

EXPOSE 8080

ENTRYPOINT  ["./initializer.sh"]