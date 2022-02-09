FROM python:3.8-slim-buster

RUN apt-get update && \
    apt-get upgrade && \
    apt-get install -y git bash

RUN python3.8 -m pip install --upgrade pip

RUN ln -s /usr/bin/python3.8 /usr/bin/python & \
    ln -s /usr/bin/pip3 /usr/bin/pip

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /simphony/osp-core

RUN git clone https://github.com/simphony/osp-core.git temp && \
    cd temp/ && \
    git checkout v3.6.0 && \
    python -m pip install . && \
    cd .. && \
    rm -rf temp

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