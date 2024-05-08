FROM python:3.8.19-alpine3.19

RUN mkdir /opt/api

ENV PYTHONPATH=/usr/lib/python3.8/site-packages

WORKDIR /opt/api

COPY api.py titanic.csv build.requirements.txt /opt/api/

RUN apk update && apk add --no-cache --update sqlite cmake g++

RUN python -m pip install --upgrade pip && pip install -r build.requirements.txt 

EXPOSE 5000

CMD ["flask", "--app", "api.py", "run", "--host=0.0.0.0", "--debug"]