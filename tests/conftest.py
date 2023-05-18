import time
import subprocess
import signal
import os
import pytest
from osp.core.namespaces import mods

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
AGENT_TEST_HOST="127.0.0.1"
AGENT_TEST_PORT="5000"
FLASK_APP="app.py"

def pytest_configure(config):
  # this is run before any tests and sets env vars
  # required for the tests
  os.environ['MODS_AGENT_HOST'] = AGENT_TEST_HOST
  os.environ['MODS_AGENT_PORT'] = AGENT_TEST_PORT
  os.environ['MODS_AGENT_BASE_URL'] = f"http://{AGENT_TEST_HOST}:{AGENT_TEST_PORT}"
  os.environ['FLASK_APP'] = FLASK_APP
  return config


@pytest.fixture(scope="session", autouse=True)
def mods_mock_agent():
    """
        This fixture starts a mock_agent flask server on a
        different process for all the tests. The server must be run
        on a different process as otherwise it would block the tests
        execution. Additionally, a care is taken to start the server
        with the the same python interpreter as the one used to run
        the tests.
        Thanks to the session scope the fixture is run only once
        prior to any tests.
    """
    agent_proc_args = []
    # check if tests are run using python virt env
    virt_env = os.environ.get('VIRTUAL_ENV')
    if virt_env is not None:
        if os.name == 'nt':
            # activate virt env for windows
            agent_proc_args.extend([
                os.path.join(virt_env,"Scripts","activate.bat"), "&&"
            ]
            )
        else:
            # activate virt env for unix
            agent_proc_args.extend([".",os.path.join(virt_env,"bin","activate"), ";"])

    host=os.environ['MODS_AGENT_HOST']
    port=os.environ['MODS_AGENT_PORT']
    agent_proc_args.extend([
        "python",
        "-m",
        "flask",
        "run",
        "-h",
        host,
        "-p",
        port])

    agent_proc_args = ' '.join(agent_proc_args)
    cwd = os.path.abspath(os.path.join(THIS_DIR, "mods_mock_agent", "api"))
    agent_proc = subprocess.Popen(
        args = agent_proc_args,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True,
        start_new_session=True,
        cwd = cwd,
    )

    # Give the server time to start
    time.sleep(2)
    # Check if started successfully
    yield agent_proc
    # Shut it down at the end of the pytest session
    if os.name == 'nt':
        subprocess.call(['taskkill', '/F', '/T', '/PID', str(agent_proc.pid)])
    else:
        os.killpg(os.getpgid(agent_proc.pid), signal.SIGTERM)

@pytest.fixture()
def moo_data():
    moo_simulation = mods.MultiObjectiveSimulation()
    moo_algorithm = mods.Algorithm(name="algorithm1", type="MOO", maxNumberOfResults= 10)
    moo_algorithm.add(
        mods.Variable(name="var1", type="input"),
        mods.Variable(name="var2", type="input"),
        mods.Variable(name="var3", type="input"),
        mods.Variable(name="var4", type="output", objective="Maximise", minimum="0.5", weight="0.5"),
        mods.Variable(name="var5", type="output", objective="Minimise", maximum="1.5", weight="0.1"),
        mods.Variable(name="var6", type="output", objective="Maximise", minimum="2.5", weight="0.7"),
    )

    moo_simulation.add(moo_algorithm)

    example_data = [
        ["var1", "var2", "var3", "var4", "var5", "var6"],
        [0.1, 0.4, 0.5, 0.1, 1.2, 2.5],
        [0.3, 0.9, 0.1, 0.9, 2.0, 3.0],
        [0.6, 0.0, 0.2, 0.1, 1.0, 1.2],
        [0.1, 0.1, 0.3, 0.7, 1.6, 2.1],
        [0.2, 0.8, 0.5, 0.1, 1.7, 4.0],
    ]

    example_data_header = example_data[0]
    example_data_values = example_data[1:]

    input_data = mods.InputData()

    for row in example_data_values:
        data_point = mods.DataPoint()
        for header, value in zip(example_data_header, row):
            data_point.add(
                mods.DataPointItem(name=header, value=value),
                rel=mods.hasPart,
            )
        input_data.add(data_point, rel=mods.hasPart)

    moo_simulation.add(input_data)
    return moo_simulation

@pytest.fixture()
def moo_analytic_data():
    moo_simulation = mods.MultiObjectiveSimulation()
    moo_algorithm = mods.Algorithm(
        name="algorithm1", type="MOO", maxNumberOfResults=10, saveSurrogate=False
    )
    moo_algorithm.add(
        mods.Variable(name="var1", type="input"),
        mods.Variable(name="var2", type="input"),
        mods.Variable(name="var3", type="input"),
        mods.Variable(name="var4", type="output", objective="Maximise", minimum="0.5", weight="0.5"),
        mods.Variable(name="var5", type="output", objective="Minimise", maximum="1.5", weight="0.1"),
        mods.Variable(name="var6", type="output", objective="Maximise", minimum="2.5", weight="0.7"),
    )

    moo_simulation.add(moo_algorithm)


    # Add numerical input data
    # -------------------------------
    example_data = [
        ["var1", "var2", "var3"],
        [0.1, 0.4, 0.5],
        [0.3, 0.9, 0.1],
        [0.6, 0.0, 0.2],
        [0.1, 0.1, 0.3],
        [0.2, 0.8, 0.5],
        [0.2, 0.8, 0.5],
        [0.2, 0.8, 0.5],
    ]

    example_data_header = example_data[0]
    example_data_values = example_data[1:]

    input_data = mods.InputData()

    for row in example_data_values:
        data_point = mods.DataPoint()
        for header, value in zip(example_data_header, row):
            data_point.add(
                mods.DataPointItem(name=header, value=value),
                rel=mods.hasPart,
            )
        input_data.add(data_point, rel=mods.hasPart)

    moo_simulation.add(input_data)
    # -------------------------------

    # Add analytical model
    # -------------------------------
    example_functions = {
            "var4": "var1 * var2",
            "var5": "var1 + var3",
            "var6": "exp(var1)-var2/2.0",
        }

    analytic_model = mods.AnalyticModel()

    for key, value in example_functions.items():
        analytic_model.add(
            mods.Function(name=key, formula=value),
            rel=mods.hasPart
        )

    moo_simulation.add(analytic_model)
    return moo_simulation