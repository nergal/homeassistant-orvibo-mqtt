ARG BUILD_FROM
FROM $BUILD_FROM

ENV LANG C.UTF-8

RUN apk update
RUN apk add --no-cache python3 py3-pip git python3-dev libffi-dev openssl-dev gcc libc-dev rust cargo
RUN pip install poetry

ADD src /app
ADD etc /etc
COPY ./poetry.lock /app
COPY ./pyproject.toml /app
RUN cd /app && poetry install --no-dev

COPY ./scripts/run.sh /

RUN chmod a+x /run.sh

CMD [ "/run.sh" ]