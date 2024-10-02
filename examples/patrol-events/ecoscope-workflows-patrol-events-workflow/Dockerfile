# [generated]
# by = { compiler = "ecoscope-workflows-core", version = "9999" }
# from-spec-sha256 = "5f829d8715e0d1d99e9bd17ffdbd4cdf3add65c43661fae0725e495fc4d20c66"


FROM bitnami/minideb:bullseye as fetch
RUN apt-get update && apt-get install -y curl
RUN curl -fsSL https://pixi.sh/install.sh | bash

FROM bitnami/minideb:bullseye as install
COPY --from=fetch /root/.pixi /root/.pixi
ENV PATH="/root/.pixi/bin:$PATH"
COPY .tmp /tmp
WORKDIR /app
COPY . .
RUN rm -rf .tmp
RUN pixi install -e default --locked

FROM install as app
ENV PORT 8080
ENV CONCURRENCY 1
ENV TIMEOUT 600
CMD pixi run -e default \
    uvicorn --host 0.0.0.0 --port $PORT --workers $CONCURRENCY --timeout-graceful-shutdown $TIMEOUT ecoscope_workflows_patrol_events_workflow.app:app

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
