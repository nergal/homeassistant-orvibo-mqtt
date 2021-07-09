ARG BUILD_FROM
FROM $BUILD_FROM
WORKDIR /app
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

COPY ./Pipfile /app
COPY ./Pipfile.lock /app
RUN pipenv install --system

ADD src /app
ADD etc /app/etc

COPY ./scripts/run.sh /

RUN chmod a+x /run.sh

CMD [ "/run.sh" ]