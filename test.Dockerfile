FROM python:3.8.19-alpine3.19

RUN mkdir /opt/api

ENV PYTHONPATH=/usr/lib/python3.8/site-packages

WORKDIR /opt/api

COPY api.py titanic.csv test.requirements.txt create_database_from_csv.py /opt/api/

RUN apk update && apk add --no-cache --update lapack musl-dev linux-headers sqlite cmake g++

RUN python -m pip install --upgrade pip && pip install -r test.requirements.txt 

RUN python create_database_from_csv.py

EXPOSE 5000

CMD ["flask", "--app", "api.py", "run", "--host=0.0.0.0"]

 
