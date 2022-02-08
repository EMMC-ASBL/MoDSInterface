#!/bin/bash

# run the production mods mock agent
docker-compose up -d mods_mock_agent_production

# run the mods simphony wrapper
docker-compose run wrapper_agent bash