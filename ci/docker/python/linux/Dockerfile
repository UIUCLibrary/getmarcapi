ARG PYTHON_VERSION="latest"
FROM python:${PYTHON_VERSION} AS base_image

#==============================================================================
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

RUN mkdir -p /home/user/.sonar/ && chmod -R 777 /home/user/

