ARG PIP_CACHE_DIR=/.cache/pip
FROM ubuntu:20.04 as wheel_builder_base
COPY ci/docker/python/tox/apt-packages.txt /tmp/apt-packages.txt
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN apt-get update && \
    apt-get install --no-install-recommends -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    < /tmp/apt-packages.txt xargs apt-get install --no-install-recommends -y && \
    npm cache clean -f && \
    npm install -g n && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN n stable -y && \
    npm install -g npm && \
    mkdir /.npm && \
    chmod 777 /.npm


ARG PIP_CACHE_DIR
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
COPY requirements/ /tmp/python_requirements/requirements/
COPY requirements-ci.txt /tmp/python_requirements

RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install --no-cache-dir -r /tmp/python_requirements/requirements-ci.txt

RUN mkdir -p ${PIP_CACHE_DIR} && chmod -R 777 ${PIP_CACHE_DIR} && \
    chmod -R 777 /.cache
ENV PIP_CACHE_DIR = ${PIP_CACHE_DIR}
WORKDIR /src
CMD ["tox", "--workdir", "/tmp/tox/", "-vv", "--parallel--safe-build", "--recreate"]
