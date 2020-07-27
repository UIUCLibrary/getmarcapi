# syntax = docker/dockerfile:1.0-experimental
FROM python:3.8 as builder
#RUN apk add --no-cache \
#    gcc \
#    musl-dev \
#    linux-headers \
#    libxml2-dev \
#    libxslt-dev

RUN python -m pip install pip --upgrade && \
    pip install --upgrade setuptools && \
    pip install wheel pep517
COPY getmarcapi /src/getmarcapi/
COPY pyproject.toml README.rst setup.cfg setup.py   /src/
WORKDIR /src

ARG PIP_INDEX_URL
RUN pip wheel gunicorn python-dotenv --wheel-dir=/wheels
RUN pip wheel . --wheel-dir=/wheels

FROM python:3.8

COPY --from=builder /wheels/*.whl /wheels/
RUN pip install --find-links=/wheels --no-index getmarcapi
RUN pip install --find-links=/wheels --no-index python-dotenv
ENV FLASK_ENV=development
ENV FLASK_DEBUG = 1
EXPOSE 5000
# TODO: add config file to include the domain and the apikey
#RUN --mount=type=secret,id=config cat /run/secrets/config>.env
CMD python -m getmarcapi

