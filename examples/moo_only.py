import logging
from osp.core.namespaces import mods, cuba
from osp.core.utils import pretty_print, export_cuds
import osp.core.utils.simple_search as search
import osp.wrappers.sim_cmcl_mods_wrapper.mods_session as ms
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())
logger.handlers[0].setFormatter(
    logging.Formatter("%(levelname)s %(asctime)s [%(name)s]: %(message)s")
)


def MOOonly_example(surrogateToLoad="mods-sim-8606989784878733752"):
    logger.info(
        "################  Start: MoDS MOO only Example ################")
    logger.info("Loading enviroment variables")
    load_dotenv()
    logger.info("Setting up the simulation inputs")

    moo_simulation = mods.MultiObjectiveSimulationOnly()
    hdmr_algorithm = mods.Algorithm(
        name="algorithm1", type="GenSurrogateAlg", surrogateToLoad=surrogateToLoad, saveSurrogate=False)
    moo_simulation.add(hdmr_algorithm)
    moo_algorithm = mods.Algorithm(
        name="algorithm2", type="MOO", maxNumberOfResults=10, saveSurrogate=False)
    moo_algorithm.add(
        mods.Variable(name="var1", type="input"),
        mods.Variable(name="var2", type="input"),
        mods.Variable(name="var3", type="input"),
        mods.Variable(name="var4", type="output",
                      objective="Maximise", minimum="0.5", weight="0.5"),
        mods.Variable(name="var5", type="output",
                      objective="Minimise", maximum="1.5", weight="0.1"),
        mods.Variable(name="var6", type="output",
                      objective="Maximise", minimum="2.5", weight="0.7"),
    )

    moo_simulation.add(moo_algorithm)

    pareto_front = None

    # export_cuds(moo_simulation, "examples/inputs/moo_only_input.ttl")

    logger.info("Invoking the wrapper session")
    # Construct a wrapper and run a new session
    with ms.MoDS_Session() as session:
        wrapper = cuba.wrapper(session=session)
        wrapper.add(moo_simulation, rel=cuba.relationship)
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

        # export_cuds(moo_simulation, "examples/outputs/moo_only_output.ttl")

    logger.info("################  End: MoDS MOO only Example ################")

    return pareto_front


if __name__ == "__main__":
    MOOonly_example()
