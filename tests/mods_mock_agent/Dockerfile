FROM python:3.8.3-alpine as base

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /tmp
RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r /tmp/requirements.txt

WORKDIR /app
COPY ./api/ .

ENV FLASK_APP=app.py

############### ANALYZE ###############
FROM base as analyze
RUN apk update \
  && apk add --no-cache --virtual build-deps gcc musl-dev build-base postgresql-dev \
  && pip install --upgrade --trusted-host pypi.org --trusted-host files.pythonhosted.org pip \
  && pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org flake8 bandit safety pylint

WORKDIR /app
CMD flake8 . --count --show-source --statistics --max-line-length 88 ; \
    bandit -r . ; \
    pylint --disable=E0401 .

############### DEBUGGER ###############
FROM base as debug
RUN pip install debugpy --trusted-host pypi.org --trusted-host files.pythonhosted.org

WORKDIR /app
CMD python -m debugpy --listen 0.0.0.0:5678 --wait-for-client -m flask run -h 0.0.0.0 -p 5000

############### DEV w/ HOT RELOAD ###############
FROM base as development

WORKDIR /app
ENV FLASK_ENV=development

CMD python -m flask run -h 0.0.0.0 -p 5000

############### PRODUCTION #############
FROM base as production
WORKDIR /app
RUN pip install --upgrade --trusted-host pypi.org --trusted-host files.pythonhosted.org gunicorn
ENV FLASK_ENV=production

CMD gunicorn --bind 0.0.0.0:5000 '__init__:create_app()'