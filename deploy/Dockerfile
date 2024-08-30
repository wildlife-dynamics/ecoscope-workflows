# stage 1: build the environment with micromamba
FROM mambaorg/micromamba:latest as build

ARG ENVFILE=environment.yml
COPY $ENVFILE /opt/environment.yml

RUN --mount=type=bind,source=output,target=/opt/rattler-output \
    --mount=type=cache,target=/opt/conda/pkgs \
    micromamba create --file /opt/environment.yml --name env \
    -c file:///opt/rattler-output \
    -c conda-forge \
    --yes
RUN micromamba install -n env pytest -c conda-forge --yes
RUN micromamba clean --all -f --yes

# stage 2: clean the environment by removing unnecessary files
# that cannot otherwise (currently) be excluded by micromamba create
FROM mambaorg/micromamba:latest as clean

COPY --from=build /opt/conda/envs/env /opt/conda/envs/env

USER root
RUN rm -rf /opt/conda/envs/env/conda-meta

RUN export BIN=/opts/conda/envs/env/bin \
    && rm -rf $BIN/h4* \
    && rm -rf $BIN/h5* \
    && rm -rf $BIN/hdf* \
    && rm -rf $BIN/ipython* \
    && rm -rf $BIN/openssl \
    && rm -rf $BIN/pdf* \
    && rm -rf $BIN/pip* \
    && rm -rf $BIN/sqlite3 \
    && rm -rf $BIN/wheel

RUN export SHARE=/opt/conda/envs/env/share \
    && rm -rf $SHARE/bash-completion \
    && rm -rf $SHARE/cmake \
    && rm -rf $SHARE/doc \
    && rm -rf $SHARE/examples \
    && rm -rf $SHARE/hdf5_examples \
    && rm -rf $SHARE/jupyter \
    && rm -rf $SHARE/man \
    && rm -rf $SHARE/pg_* \
    && rm -rf $SHARE/postgres* \
    && rm -rf $SHARE/psql* \
    && rm -rf $SHARE/terminfo

RUN export SITEPKGS=/opt/conda/envs/env/lib/python3.12/site-packages \
    && rm -rf $SITEPKGS/numba/tests \
    && rm -rf $SITEPKGS/pip* \
    && rm -rf $SITEPKGS/setuptools* \
    && rm -rf $SITEPKGS/wheel* \
    && rm -rf $SITEPKGS/xarray*

RUN cd /opt/conda \
    && find -name '*.a' -delete \
    && find -name '__pycache__' -type d -exec rm -rf '{}' '+'

USER $MAMBA_USER

# stage 3: create a testable distroless runtime image
# this is testable because we haven't removed pytest yet
FROM gcr.io/distroless/base-debian12 as testable_runtime

COPY --from=clean /opt/conda/envs/env /env


# stage 4: unzip the lithops proxy
FROM python:3.10-slim-buster as unzip_proxy

RUN apt-get update && apt-get install -y \
    zip \
    && rm -rf /var/lib/apt/lists/*

ENV APP_HOME /lithops
WORKDIR $APP_HOME
# assumes the build context is running the lithops runtime build command
# in a context with the same lithops version as the one in the container (?)
COPY lithops_cloudrun.zip .
RUN unzip lithops_cloudrun.zip && rm lithops_cloudrun.zip


# stage 5: copy the lithops proxy into the distroless
# image and remove test dependencies
FROM testable_runtime as serve

COPY --from=unzip_proxy /lithops /lithops

ENV CONCURRENCY 1
ENV TIMEOUT 600
WORKDIR /lithops

CMD /env/bin/gunicorn --bind :$PORT --workers $CONCURRENCY --timeout $TIMEOUT lithopsproxy:proxy
