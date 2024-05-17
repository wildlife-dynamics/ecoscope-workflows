FROM python:3.11

WORKDIR /ecoscope-workflows

RUN python -m pip install -U setuptools setuptools_scm[toml]
ENV SETUPTOOLS_SCM_PRETEND_VERSION="0.1.0"
COPY ecoscope_workflows ./ecoscope_workflows
COPY pyproject.toml .
RUN pip install --no-cache-dir -e .
