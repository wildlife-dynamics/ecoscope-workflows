FROM mambaorg/micromamba:latest as build

ARG ENVFILE=environment.yml
ARG ENVNAME=lithops-worker

USER root
RUN apt-get update && apt-get install -y \
        zip \
        && rm -rf /var/lib/apt/lists/*
USER $MAMBA_USER

COPY $ENVFILE ./
RUN --mount=type=bind,source=output,target=/opt/rattler-output/ \
    micromamba create --file $ENVFILE --name $ENVNAME --yes
RUN micromamba clean --all -f --yes

ENV CONCURRENCY 1
ENV TIMEOUT 600
ENV ENVNAME $ENVNAME

# Copy Lithops proxy and lib to the container image.
# ENV APP_HOME /lithops
# WORKDIR $APP_HOME

# COPY lithops_cloudrun.zip .
# RUN unzip lithops_cloudrun.zip && rm lithops_cloudrun.zip

# CMD micromamba run -n $ENVNAME gunicorn --bind :$PORT --workers $CONCURRENCY --timeout $TIMEOUT lithopsproxy:proxy
