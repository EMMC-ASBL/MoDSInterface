#!/bin/bash
#
# Description: This script creates a docker image that includes the osp-core
#              and the app4 use case wrapper
#
# Run Information: This script should be run manually.

# build the production ready mods mock agent
# and the mods simphony wrapper
docker-compose --profile production build