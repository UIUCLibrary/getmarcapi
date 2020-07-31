FROM python:3.8-slim as builder

RUN python -m pip install pip --upgrade && \
    pip install --upgrade setuptools && \
    pip install wheel pep517
COPY getmarcapi /src/getmarcapi/
COPY pyproject.toml README.rst setup.cfg setup.py   /src/
WORKDIR /src

ARG PIP_INDEX_URL
RUN pip wheel --wheel-dir=/wheels gunicorn python-dotenv
RUN pip wheel --wheel-dir=/wheels .

FROM python:3.8-slim

COPY --from=builder /wheels/*.whl /wheels/
RUN pip install --find-links=/wheels --no-index python-dotenv gunicorn
RUN pip install --find-links=/wheels --no-index getmarcapi
EXPOSE 5000
WORKDIR /app
COPY api.cfg /app/settings.cfg
ENV GETMARCAPI_SETTINGS=/app/settings.cfg
RUN python -m getmarcapi --check
CMD gunicorn getmarcapi.app:app --bind 0.0.0.0:5000 --log-level=debug

