FROM alpine:latest

RUN mkdir /app

COPY app.py \
     docker_compose_log.py \
     docker_compose_output.py \
     requirements.txt \
     startup.sh /app/
COPY public /app/public
COPY templates /app/templates

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

FROM docker:latest

RUN apk add --no-cache bash \
    python

COPY --from=0 /app /app

WORKDIR /app

CMD ["./startup.sh"]
