<img align="right" src="cmcl_logo.png" alt="CMCL Logo">

# OntoTrans MoDS Wrappper

[SimPhoNy](https://github.com/simphony)-based implementation of the OntoTrans MoDS wrapper.

The wrapper currently supports the Multi Objective Optimization feature (MOO). The wrapper workflow is as follows:
- semantic (CUDS) to syntactic (JSON) translation of the input data
- triggering the MOO simulation by sending the translated input data via HTTP request to the MoDS web agent
- checking the simulation status
- collection of the simulation outputs from the MoDS web agent
- syntactic (JSON) to semantic (CUDS) translation of the simulation results

The mock version of the MoDS web agent is additionally provided for testing and debugging purposes.

# Requirements
- Python 3.8 (or higher)
- [SimPhoNy](https://github.com/simphony/osp-core)

# Installation - docker

A convenience `docker_install.sh` script has been provided that creates the following two docker images:

- `cmcl/mods_mock_agent`
- `cmcl/sim_cmcl_mods_wrapper`

The created images contain the mock MoDS web agent and MoDS wrapper applications and all the required dependencies.

# Installation - local

Please follow these steps to install the wrapper on your machine:

1. Install `SimPhoNy` (for details, see [https://simphony.readthedocs.io/en/latest/installation.html](https://simphony.readthedocs.io/en/latest/installation.html))
```bash
    # install the osp-core v3.6.0
    python -m pip install git+https://github.com/simphony/osp-core.git@v3.6.0
```

2. Install `sim_cmcl_mods_wrapper`
```bash
    # install the wrapper
    python -m pip install .
    # install app4 simple ontology
    pico install ontology.mods.yml
    # (optional) install the wrapper tests requirements
    python -m pip install -r tests/test_requirements.txt
```

# Usage - docker

A convenience `run_container.sh` script has been provided to easily run the MoDS wrapper. The script firstly spins up the `mods_mock_agent` container which runs the mock MoDS agent application and subsequently spins up and launches bash terminal in the `sim_cmcl_mods_wrapper` container. Once in a bash terminal, run the following command to trigger an example MOO simulation:

```bash
   python examples/app4.py
```

# Usage - local

## Enabling mock MoDS agent

The MoDS wrapper requires a running instance of the MoDS web agent that handles the actual simulation. At the moment, only the mock version of the MoDS web agent is available. The mock agent was provided to enable the MoDS wrapper testing and its integration with the OTE platform. The production ready MoDS agent is currently being developed, however, it is still recommended to use the mock agent for testing and OTE platform plumbing work. In order to enable the mock MoDS agent for the wrapper please follow these steps:

1. Install `mods_mock_agent` requirements
```bash
    cd mods_mock_agent
    python -m pip install -r requirements.txt
```
2. Run the `mods_mock_agent` instance

Unix
```bash
    cd mods_mock_agent/api
    export FLASK_APP=app.py
    python -m flask run -h 0.0.0.0 -p 5000 &
```

Windows
```cmd
    cd mods_mock_agent/api
    set FLASK_APP=app.py
    python -m flask run -h 0.0.0.0 -p 5000 &
```

3. Set the `MODS_AGENT_BASE_URL` environment variable. Note, this should define the hostname and port that the agent is running at. In case of the mock MoDS agent, please set it to the following value:

Unix
```bash
    export MODS_AGENT_BASE_URL=http://localhost:5000
```

Windows
```bash
    set export MODS_AGENT_BASE_URL=http://localhost:5000
```

## Running the example wrapper session

Once everything is installed and the MoDS web agent is configured, run the following command to trigger an example use case simulation:

```bash
   python examples/moo.py
```

# Testing

Testing is done using python's `pytest` module. The following command would, spin a local mods mock agent and run all the tests:

```bash
    pytest tests
```

# Contact
For questions, issues, or suggestions, please contact danieln@cmclinnovations.com and gbrownbridge@cmclinnovations.com