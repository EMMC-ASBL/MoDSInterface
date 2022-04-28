#!/bin/bash
#
# Description: This script creates a docker image that includes the osp-core
#              and the mods simphony wrapper
#
# Run Information: This script should be run manually.

# build the production ready mods simphony wrapper
docker-compose build