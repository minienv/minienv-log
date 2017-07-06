FROM alpine:latest

RUN mkdir /app

COPY requirements.txt /app/

WORKDIR /app

RUN apk add --no-cache bash \
    python-dev \
    build-base \
  && python -m ensurepip \
  && pip install --upgrade pip \
  && pip install virtualenv \
  && virtualenv -p python venv \
  && source venv/bin/activate \
  && venv/bin/pip install -r requirements.txt

COPY app.py \
     docker_compose_log.py \
     docker_compose_output.py \
     startup.sh /app/
COPY public /app/public
COPY templates /app/templates

FROM docker:latest

MAINTAINER Mark Watson <markwatsonatx@gmail.com>

RUN apk add --no-cache bash \
    python

COPY --from=0 /app /app

WORKDIR /app

CMD ["./startup.sh"]