FROM ubuntu:20.04 as wheel_builder_base
RUN apt update && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt update
COPY ci/docker/python/tox/apt-packages.txt /tmp/apt-packages.txt
RUN cat /tmp/apt-packages.txt | xargs apt install -y python3-pip

ARG USER_ID=1000
ARG GROUP_ID=1000

RUN groupadd -g $GROUP_ID user && \
    useradd -u $USER_ID -s /bin/sh -m -d /home/user -g user user

# ******************************************************************************
FROM wheel_builder_base as wheel_builder_py36

RUN apt install -y python3.6-dev python3.6-venv
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL

COPY ci/docker/python/shared/requirements-ci.txt /tmp/
RUN PYTHON=python3.6 && \
    $PYTHON -m pip install pip --upgrade pip && \
    $PYTHON -m pip install wheel && \
    $PYTHON -m pip wheel -w /wheels --no-cache-dir -r /tmp/requirements-ci.txt

# ==============================================================================
FROM wheel_builder_base as wheel_builder_py37
RUN apt install -y python3.7-dev python3.7-venv

ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL

COPY ci/docker/python/shared/requirements-ci.txt /tmp/
RUN PYTHON=python3.7 && \
    $PYTHON -m pip install pip --upgrade pip && \
    $PYTHON -m pip install wheel && \
    $PYTHON -m pip wheel -w /wheels --no-cache-dir -r /tmp/requirements-ci.txt
# ==============================================================================
FROM wheel_builder_base as wheel_builder_py38
RUN apt install -y python3.8-dev python3.8-venv

ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL

COPY ci/docker/python/shared/requirements-ci.txt /tmp/
RUN PYTHON=python3.8 && \
    $PYTHON -m pip install pip --upgrade pip && \
    $PYTHON -m pip install wheel && \
    $PYTHON -m pip wheel -w /wheels --no-cache-dir -r /tmp/requirements-ci.txt

# ==============================================================================
FROM wheel_builder_base

ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL

COPY --from=wheel_builder_py36 /wheels/* /wheels/
COPY --from=wheel_builder_py37 /wheels/* /wheels/
COPY --from=wheel_builder_py38 /wheels/* /wheels/
ENV PIP_FIND_LINKS=/wheels
RUN pip3 install tox

USER user
WORKDIR /src
CMD tox --workdir /tmp/tox/ -vv --parallel--safe-build --recreate