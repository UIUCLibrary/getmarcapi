ARG PIPX_HOME=/pipx
ARG PIP_CACHE_DIR=/.cache/pip

FROM ubuntu:22.04 AS wheel_builder_base
COPY ci/docker/python/tox/apt-packages.txt /tmp/apt-packages.txt
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN apt-get update && \
    apt-get install -y software-properties-common gpg-agent --no-install-recommends && \
    add-apt-repository ppa:deadsnakes/ppa && \
    DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get -y install tzdata && \
    apt-get update && \
     < /tmp/apt-packages.txt xargs apt-get install -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN npm cache clean -f && \
    npm install -g n
RUN n stable -y && \
    npm install -g npm && \
    mkdir /.npm && \
    chmod 777 /.npm


ARG PIP_CACHE_DIR
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
COPY requirements/ /tmp/python_requirements/requirements/
COPY requirements-dev.txt /tmp/python_requirements

RUN python3 -m pip install --upgrade pip && \
    pip3 install --no-cache-dir --ignore-installed  -r /tmp/python_requirements/requirements-dev.txt

RUN mkdir -p ${PIP_CACHE_DIR} && chmod -R 777 ${PIP_CACHE_DIR} && \
    chmod -R 777 /.cache
ENV PIP_CACHE_DIR = ${PIP_CACHE_DIR}

ARG PIPX_HOME
ENV PIPX_HOME=${PIPX_HOME}
ENV PIPX_BIN_DIR=${PIPX_HOME}/bin
RUN pip3 install --no-cache-dir pipx && \
    pipx ensurepath && \
    mkdir -p $PIPX_HOME  && chmod -R 777 $PIPX_HOME
RUN PIPX_HOME=/opt/pipx PIPX_BIN_DIR=/usr/local/bin pipx install 'devpi-client<7.0' &&  \
    PIPX_HOME=/opt/pipx PIPX_BIN_DIR=/usr/local/bin pipx install pip-audit



WORKDIR /src
CMD ["tox", "--workdir", "/tmp/tox/", "-vv", "--parallel--safe-build", "--recreate"]
