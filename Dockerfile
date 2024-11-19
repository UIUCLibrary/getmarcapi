FROM python:3.11-slim AS base_image

FROM base_image AS builder
RUN apt update -y && apt install -y npm
RUN python -m pip install pip --upgrade && \
    pip install --upgrade setuptools && \
    pip install wheel build
COPY getmarcapi /src/getmarcapi/
COPY src /src/src/
COPY pyproject.toml README.rst README.md setup.py MANIFEST.in requirements.txt /src/
WORKDIR /src
COPY package.json package-lock.json webpack.config.js ./
RUN npm install

ARG PIP_INDEX_URL
ARG PIP_EXTRA_INDEX_URL
COPY requirements.txt ./requirements.txt
RUN pip wheel --wheel-dir=/wheels -r /src/requirements.txt
RUN python -m build --wheel --outdir /wheels

FROM base_image

COPY --from=builder /wheels/*.whl /wheels/
COPY requirements.txt ./requirements.txt
RUN pip install --find-links=/wheels --no-index -r requirements.txt
RUN pip install --find-links=/wheels --no-index getmarcapi
EXPOSE 5000
WORKDIR /app
COPY api.cfg /app/settings.cfg
ENV GETMARCAPI_SETTINGS=/app/settings.cfg
RUN python -m getmarcapi --check
CMD gunicorn getmarcapi.app:app --bind 0.0.0.0:5000 --log-level=debug

