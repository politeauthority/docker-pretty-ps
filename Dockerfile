FROM frolvlad/alpine-python3

RUN apk add --no-cache \
    bash \
    python3 \
    python3-dev \
    py-pip \
    && rm -rf /var/cache/apk/*

WORKDIR /opt/docker-pretty-ps/


ADD ./ /opt/docker-pretty-ps
RUN pip3 install -r tests/requirements.txt
