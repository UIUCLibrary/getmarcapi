FROM ubuntu:20.04 as wheel_builder_base
COPY ci/docker/python/tox/apt-packages.txt /tmp/apt-packages.txt
RUN apt update && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt update && \
    cat /tmp/apt-packages.txt | xargs apt install -y

RUN npm cache clean -f && \
    npm install -g n

RUN n stable -y && \
    npm install -g npm && \
    mkdir /.npm && \
    chmod 777 /.npm

ARG USER_ID=1000
ARG GROUP_ID=1000

RUN if id $USER_ID ; then \
        echo 'Existing user id found: Creating an alias' ;\
        groupadd --non-unique --gid $GROUP_ID user ; \
        useradd  --non-unique --uid $USER_ID -s /bin/sh -m -d /home/user -g user user  ; \
    else \
        echo "Creating user id for $USER_ID" ;\
        groupadd -g $GROUP_ID user ; \
        echo "Create GROUP_ID $GROUP_ID" ;\
        useradd  -u $USER_ID -s /bin/sh -m -d /home/user -g user user ;\
    fi

# ******************************************************************************
FROM wheel_builder_base as wheel_builder_py36

ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL

COPY ci/docker/python/shared/requirements-ci.txt /tmp/
RUN PYTHON=python3.6 && \
    $PYTHON -m pip install pip --upgrade pip && \
    $PYTHON -m pip install wheel && \
    $PYTHON -m pip wheel -w /wheels --no-cache-dir -r /tmp/requirements-ci.txt

# ==============================================================================
FROM wheel_builder_base as wheel_builder_py37

ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL

COPY ci/docker/python/shared/requirements-ci.txt /tmp/
RUN PYTHON=python3.7 && \
    $PYTHON -m pip install pip --upgrade pip && \
    $PYTHON -m pip install wheel && \
    $PYTHON -m pip wheel -w /wheels --no-cache-dir -r /tmp/requirements-ci.txt
# ==============================================================================
FROM wheel_builder_base as wheel_builder_py38

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
RUN python3 -m pip install pip --upgrade && \
    pip3 install tox

USER user
WORKDIR /src
CMD tox --workdir /tmp/tox/ -vv --parallel--safe-build --recreate