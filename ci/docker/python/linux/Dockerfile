ARG PYTHON_VERSION="3.11"
ARG PIP_FIND_LINKS=/wheels/
FROM python:${PYTHON_VERSION} as base_image
#==============================================================================
FROM base_image AS SONAR_BUILDER
RUN apt-get update && \
    apt-get install -y unzip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
ENV SONAR_SCANNER_VERSION=4.6.2.2472
ARG SONAR_SCANNER_HOME=/opt/sonar/${SONAR_SCANNER_VERSION}-linux
ENV SONAR_USER_HOME=/opt/sonar/.sonar
RUN curl --create-dirs -sSLo /tmp/sonar-scanner.zip \
        https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-$SONAR_SCANNER_VERSION-linux.zip && \
    unzip -o /tmp/sonar-scanner.zip -d /opt/sonar/ && \
    rm /tmp/sonar-scanner.zip && \
    mkdir -p $SONAR_USER_HOME/cache && \
    chmod -R 777 "${SONAR_USER_HOME}" &&\
    ln -s /opt/sonar/sonar-scanner-$SONAR_SCANNER_VERSION-linux/bin/sonar-scanner /usr/local/bin/sonar-scanner && \
    which sonar-scanner

FROM base_image as wheel_builder
ARG PIP_FIND_LINKS
ARG PIP_EXTRA_INDEX_URL
COPY requirements-ci.txt /requirements/
COPY requirements/ /requirements/requirements/

ARG PIP_FIND_LINKS
RUN mkdir -p ${PIP_FIND_LINKS} &&  \
    pip wheel --wheel-dir=${PIP_FIND_LINKS} --no-cache-dir -r /requirements/requirements-ci.txt


FROM base_image
RUN apt-get update &&  \
    apt-get install -y npm &&  \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN npm cache clean -f && \
    npm install -g n

RUN n stable -y && \
    npm install -g npm && \
    mkdir /.npm && \
    chmod 777 /.npm
COPY --from=SONAR_BUILDER /opt/sonar /opt/sonar/
ENV SONAR_SCANNER_VERSION=4.6.2.2472
ARG SONAR_SCANNER_HOME=/opt/sonar/${SONAR_SCANNER_VERSION}-linux
ENV SONAR_USER_HOME=/opt/sonar/.sonar
RUN ln -s /opt/sonar/sonar-scanner-${SONAR_SCANNER_VERSION}-linux/bin/sonar-scanner /usr/local/bin/sonar-scanner && \
    which sonar-scanner
RUN mkdir -p /home/user/.sonar/ && chmod -R 777 /home/user/


ARG PIP_FIND_LINKS
ARG PIP_EXTRA_INDEX_URL
ARG PIP_TRUSTED_HOST
COPY --from=wheel_builder ${PIP_FIND_LINKS}/* ${PIP_FIND_LINKS}/
COPY --from=wheel_builder requirements/ /requirements
RUN pip install --no-index --no-cache-dir --find-links=${PIP_FIND_LINKS} \
    -r /requirements/requirements-ci.txt

ENV PIP_FIND_LINKS=${PIP_FIND_LINKS}

ENV MYPYPATH=/mypystubs
RUN stubgen -p uiucprescon.getmarc2 -o $MYPYPATH
