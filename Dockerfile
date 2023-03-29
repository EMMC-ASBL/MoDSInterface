FROM python:3.8-slim-buster

RUN apt-get install -y bash

RUN python3.8 -m pip install --upgrade pip

RUN ln -s /usr/bin/python3.8 /usr/bin/python & \
    ln -s /usr/bin/pip3 /usr/bin/pip

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /simphony/osp-core

WORKDIR /simphony/mods-wrapper
COPY ./LICENSE.md .
COPY ./cmcl_logo.png .
COPY ./ontology.mods.yml .
COPY ./osp ./osp
COPY ./setup.py .
COPY ./examples ./examples
COPY ./tests ./tests
COPY ./README.md .
COPY ./.env .

ARG MODS_AGENT_BASE_URL
ENV MODS_AGENT_BASE_URL $MODS_AGENT_BASE_URL

RUN python -m pip install .
RUN python -m pip install -r tests/test_requirements.txt
RUN pico install ontology.mods.yml

WORKDIR /app
COPY . .
ENTRYPOINT hypercorn app.main:app --bind 0.0.0.0:8080 --log-level debug --reload