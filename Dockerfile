FROM alpine:latest

RUN apk update
RUN apk add bash
RUN apk add python-dev
RUN apk add build-base
RUN python -m ensurepip
RUN pip install --upgrade pip

RUN mkdir /app

ADD app.py /app/app.py
ADD docker_compose_log.py /app/docker_compose_log.py 
ADD docker_compose_output.py /app/docker_compose_output.py
ADD public /app/public
ADD requirements.txt /app/requirements.txt
ADD templates /app/templates

WORKDIR /app

RUN pip install virtualenv
RUN virtualenv -p python venv
RUN source venv/bin/activate
RUN venv/bin/pip install -r requirements.txt

FROM docker:latest

RUN apk update
RUN apk add bash
RUN apk add python

COPY --from=0 /app /app

ADD startup.sh /app/startup.sh

WORKDIR /app

CMD ["./startup.sh"]
