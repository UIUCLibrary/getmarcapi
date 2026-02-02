FROM python:3.11-slim AS base_image

FROM base_image AS builder
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
  --mount=type=cache,target=/var/lib/apt,sharing=locked \
  apt update -y && apt install --no-install-recommends -y npm
COPY getmarcapi /src/getmarcapi/
COPY src /src/src/
WORKDIR /src
COPY package.json package-lock.json webpack.config.js ./
RUN --mount=type=cache,target=/root/.npm npm install
RUN npm run env -- webpack --output-path=/output

#
ARG PIP_INDEX_URL
ARG PIP_EXTRA_INDEX_URL
COPY pyproject.toml uv.lock README.rst README.md setup.py MANIFEST.in /src/
RUN python -m pip install --disable-pip-version-check uv && \
  uv build --wheel --out-dir /wheels

FROM base_image

# isntall curl for heatlh checks and testing
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
  --mount=type=cache,target=/var/lib/apt,sharing=locked \
  apt update -y && apt install --no-install-recommends -y curl 


COPY --from=builder /wheels/*.whl /wheels/
WORKDIR /app
COPY  pyproject.toml uv.lock README.rst /app/
ARG PIP_INDEX_URL
ARG UV_INDEX_URL
ARG UV_CACHE_DIR=/.cache/uv
ARG UV_EXTRA_INDEX_URL
RUN --mount=type=cache,target=${UV_CACHE_DIR} \
  python -m venv uv && \
  ./uv/bin/pip install --disable-pip-version-check uv && \
  ./uv/bin/uv sync --group deploy --no-dev --no-editable --no-install-project --find-links=/wheels && \
  ./uv/bin/uv pip install --find-links=/wheels --no-index getmarcapi --no-deps
EXPOSE 5000
COPY api.cfg /app/settings.cfg
ENV GETMARCAPI_SETTINGS=/app/settings.cfg
RUN  ./.venv/bin/python -m getmarcapi --check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD curl -f http://localhost:5000 || exit 1
CMD ./.venv/bin/gunicorn getmarcapi.app:app --bind 0.0.0.0:5000 --log-level=debug

