import logging
from osp.core.namespaces import mods, cuba
from osp.core.utils import pretty_print
import osp.core.utils.simple_search as search
import osp.wrappers.sim_cmcl_mods_wrapper.mods_session as ms
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())
logger.handlers[0].setFormatter(
    logging.Formatter("%(levelname)s %(asctime)s [%(name)s]: %(message)s")
)


def MCDM_example():
    logger.info("################  Start: MoDS MCDM Example ################")
    logger.info("Setting up the simulation inputs")

    mcdm_simulation = mods.MultiCriteriaDecisionMaking()
    mcdm_algorithm = mods.Algorithm(
        name="algorithm1", type="MCDM", maxNumberOfResults=10)
    mcdm_algorithm.add(
        mods.Variable(name="var1", type="input"),
        mods.Variable(name="var2", type="input"),
        mods.Variable(name="var3", type="input"),
        mods.Variable(name="var4", type="output",
                      objective="Maximise", minimum="0.2", weight="0.5"),
        mods.Variable(name="var5", type="output",
                      objective="Minimise", maximum="2.0", weight="0.1"),
        mods.Variable(name="var6", type="output",
                      objective="Maximise", minimum="2.0", weight="0.7"),
    )

    mcdm_simulation.add(mcdm_algorithm)

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

    mcdm_simulation.add(input_data)

    logger.info("Invoking the wrapper session")
    # Construct a wrapper and run a new session
    with ms.MoDS_Session() as session:
        load_dotenv()
        wrapper = cuba.wrapper(session=session)
        wrapper.add(mcdm_simulation, rel=cuba.relationship)
        wrapper.session.run()

        pareto_front = search.find_cuds_objects_by_oclass(
            mods.ParetoFront, wrapper, rel=None
        )
        job_id = search.find_cuds_objects_by_oclass(
            mods.JobID, wrapper, rel=None
        )

        logger.info("Printing the simulation results.")

        if pareto_front:
            pretty_print(pareto_front[0])
        if job_id:
            pretty_print(job_id[0])

    logger.info("################  End: MoDS MCDM Example ################")

    return job_id


if __name__ == "__main__":
    MCDM_example()
