FROM python:3.11.3-alpine3.18 AS backend
COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt
ADD . /code
WORKDIR /code
CMD gunicorn -w 1 -b 0.0.0.0:40001 --worker-class gevent backend.server:app

FROM python:3.11.3-alpine3.18 AS worker
COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt
ADD . /code
WORKDIR /code
CMD python -m worker
