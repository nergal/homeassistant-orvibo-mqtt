ARG BUILD_FROM
FROM $BUILD_FROM

ENV LANG C.UTF-8 \
  PYTHONFAULTHANDLER=1 \
  PYTHONHASHSEED=random \
  PYTHONDONTWRITEBYTECODE=1 \
  # pip:
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100

RUN apk add --no-cache python3 py3-pip git jq
RUN pip install pipenv

COPY ./Pipfile* /
RUN pipenv install --system

ADD rootfs /

RUN chmod a+x /usr/bin/orvibo_mqtt_daemon.sh

CMD [ "/usr/bin/orvibo_mqtt_daemon.sh" ]