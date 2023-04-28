FROM python:3.9-slim-buster AS develop

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git bash

RUN pip install --upgrade pip

ARG YML_FILE
ENV YML_FILE ${YML_FILE}

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt
RUN pip install -r tests/test_requirements.txt
RUN pip install .
WORKDIR /app/osp/ontology
RUN pico install ${YML_FILE}

WORKDIR /app
RUN chmod 0700 ./docker_entrypoint.sh
EXPOSE 8080

ENTRYPOINT ["/app/docker_entrypoint.sh"]

########################## PRODUCTION #########################
FROM develop AS production

RUN pip install -r requirements_prod.txt