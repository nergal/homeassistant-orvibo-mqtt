ARG BUILD_FROM
FROM $BUILD_FROM

ENV LANG C.UTF-8
RUN mkdir /app
WORKDIR /app

RUN apk add --no-cache python3 py3-pip git

COPY ./data/requirements.txt /app
RUN pip3 install -r requirements.txt

ADD data /app

COPY ./data/run.sh /

RUN chmod a+x /run.sh
RUN ls -la /
RUN ls -la /app

CMD [ "/run.sh" ]