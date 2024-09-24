FROM bitnami/minideb:bullseye as fetch
RUN apt-get update && apt-get install -y curl
RUN curl -fsSL https://pixi.sh/install.sh | bash

FROM bitnami/minideb:bullseye as install
COPY --from=fetch /root/.pixi /root/.pixi
ENV PATH="/root/.pixi/bin:${PATH}"
COPY .tmp /tmp
WORKDIR /app
COPY . .
RUN rm -rf .tmp
RUN pixi install -a --locked

FROM install as test
ENTRYPOINT ["/bin/sh", "-c", "pixi run -e test \"$@\"", "--"]

FROM install as serve
CMD pixi run -e serve uvicorn serve:app --host 0.0.0.0 --port 3000

# FROM python:3.10-slim-buster AS unzip_proxy
# RUN apt-get update && apt-get install -y \
#     zip \
#     && rm -rf /var/lib/apt/lists/*
# ENV APP_HOME /lithops
# WORKDIR $APP_HOME
# assumes the build context is running the lithops runtime build command
# in a context with the same lithops version as the one in the container (?)
# COPY lithops_cloudrun.zip .
# RUN unzip lithops_cloudrun.zip && rm lithops_cloudrun.zip

# FROM install AS worker
# COPY --from=unzip_proxy /lithops /lithops
# ENV PORT 8080
# ENV CONCURRENCY 1
# ENV TIMEOUT 600
# WORKDIR /lithops
# CMD gunicorn --bind :$PORT --workers $CONCURRENCY --timeout $TIMEOUT lithopsproxy:proxy
