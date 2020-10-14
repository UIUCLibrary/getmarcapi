ARG PYTHON_VERSION="3.8"
FROM python:${PYTHON_VERSION} as wheel_builder

ARG PIP_EXTRA_INDEX_URL
ARG PIP_TRUSTED_HOST
ARG PIP_INDEX_URL
ADD ci/docker/python/shared/requirements-ci.txt /tmp/
RUN python -m pip install --upgrade pip &&  \
    pip install setuptools && \
    pip install wheel && \
    pip wheel --no-cache-dir \
        --wheel-dir=/wheels  \
        -r /tmp/requirements-ci.txt && \
    rm -rf  /root/.cache


FROM python:${PYTHON_VERSION}
#RUN apt update && apt install -y libenchant1c2a
ARG USER_ID=1000
ARG GROUP_ID=1000

RUN groupadd -g $GROUP_ID user && \
    useradd -u $USER_ID -s /bin/sh -m -d /home/user -g user user

USER user
ENV SONAR_SCANNER_VERSION=4.4.0.2170
ENV SONAR_SCANNER_HOME=/home/user/.sonar/sonar-scanner-$SONAR_SCANNER_VERSION-linux
RUN curl --create-dirs -sSLo $HOME/.sonar/sonar-scanner.zip \
        https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-$SONAR_SCANNER_VERSION-linux.zip && \
    unzip -o $HOME/.sonar/sonar-scanner.zip -d $HOME/.sonar/ && \
    rm $HOME/.sonar/sonar-scanner.zip && \
    mkdir -p /home/user/.sonar/cache && \
    chown user:user /home/user/.sonar/cache
ENV PATH=$SONAR_SCANNER_HOME/bin:$PATH
ENV SONAR_SCANNER_OPTS="-server"
USER root

COPY --from=wheel_builder /wheels /wheels/
ADD ci/docker/python/shared/requirements-ci.txt /tmp/
COPY --from=wheel_builder /wheels /wheels/
ENV PIP_FIND_LINKS=/wheels

RUN pip install --no-index --no-cache-dir --find-links=/wheels \
    -r /tmp/requirements-ci.txt
