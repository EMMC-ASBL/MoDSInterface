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

A convenience `docker_install.sh` script has been provided that creates the `cmcl/sim_cmcl_mods_wrapper` image.

```bash
    # build the cmcl/sim_cmcl_mods_wrapper image
    docker_install.sh
```

# Installation - local

Please follow these steps to install the wrapper on your machine (using the virtual environment is highly recommended):

```bash
    # install the mods wrapper
    python -m pip install .
    # install mods simple ontology
    pico install ontology.mods.yml
    # (optional) install the wrapper tests requirements
    python -m pip install -r tests/test_requirements.txt
```

# Usage

The mods wrapper can be used by either running it in a docker container or locally. In case of the docker container option, a convenience `run_container.sh` script has been provided to simplify this task:

```bash
   # run the sim_cmcl_mods_wrapper container and open its bash terminal
   run_container.sh
```

Regardless of the docker or local machine option for building and running the wrapper, trigger the following commands to run an example MOO simulations:

```bash
   python examples/moo.py
   python examples/moo_analytic.py
```

Please note that the above examples depend on the mods agent instance being up and running on CMCL servers.

# Testing

Testing is done using python's `pytest` module. The following command would, spin a local mods mock agent, that is included with the tests, and run all the tests with it:

```bash
    pytest tests
```

# Contact
For questions, issues, or suggestions, please contact danieln@cmclinnovations.com and gbrownbridge@cmclinnovations.com