FROM python:3-alpine

WORKDIR /usr/src/app


RUN apk update && \
    apk add --virtual build-deps gcc python-dev musl-dev && \
    apk add postgresql-dev

RUN pip install psycopg2

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./scrobbledownload ./scrobbledownload
COPY ./main.py ./main.py

CMD ["python", "./main.py"]