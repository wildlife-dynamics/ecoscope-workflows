FROM python:3.11

WORKDIR /ecoscope-workflows

RUN python -m pip install -U setuptools setuptools_scm[toml]
COPY ecoscope_workflows ./ecoscope_workflows
COPY pyproject.toml .
RUN SETUPTOOLS_SCM_PRETEND_VERSION="0.1.0" pip install --no-cache-dir -e .
# TODO: install ecoscope w/ conda
# RUN pip install "git+https://github.com/wildlife-dynamics/ecoscope.git"
