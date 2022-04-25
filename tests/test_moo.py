import logging
from osp.core.namespaces import mods, cuba
import osp.core.utils.simple_search as search
import osp.wrappers.sim_cmcl_mods_wrapper.mods_session as ms

# This examples aims to run the MOO MoDS case by hard-coding
# the input CUDS objects and passing them to the MoDS_Session class
# for execution.

# Set the level of the logger in OSP Core
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def test_moo():
    logger.info("################  Start: MoDS MOO Example ################")
    logger.info("Setting up the simulation inputs")

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

    logger.info("Invoking the wrapper session")
    # Construct a wrapper and run a new session
    with ms.MoDS_Session() as session:
        wrapper = cuba.wrapper(session=session)
        wrapper.add(moo_simulation, rel=cuba.relationship)
        wrapper.session.run()

        pareto_front = search.find_cuds_objects_by_oclass(
            mods.ParetoFront, wrapper, rel=None
        )

        assert pareto_front is not None
        assert len(pareto_front[0].get(oclass=mods.DataPoint)) == 10

def test_moo_analytic():
    logger.info("################  Start: MoDS MOO Analytic Example ################")
    logger.info("Setting up the simulation inputs")

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

    logger.info("Invoking the wrapper session")
    # Construct a wrapper and run a new session
    with ms.MoDS_Session() as session:
        wrapper = cuba.wrapper(session=session)
        wrapper.add(moo_simulation, rel=cuba.relationship)
        wrapper.session.run()

        pareto_front = search.find_cuds_objects_by_oclass(
            mods.ParetoFront, wrapper, rel=None
        )

        assert pareto_front is not None
        assert len(pareto_front[0].get(oclass=mods.DataPoint)) == 10