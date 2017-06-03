FROM docker:latest

RUN apk update
RUN apk add bash
RUN apk add python3-dev
RUN apk add build-base
RUN python3 -m ensurepip
RUN pip3 install --upgrade pip

RUN mkdir /app

ADD app.py /app/app.py
ADD docker_compose_log.py /app/docker_compose_log.py 
ADD docker_compose_output.py /app/docker_compose_output.py
ADD public /app/public
ADD requirements.txt /app/requirements.txt
ADD templates /app/templates

WORKDIR /app

RUN pip3 install -r requirements.txt

CMD ["python3","app.py"]
