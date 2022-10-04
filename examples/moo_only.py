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

# This examples aims to run the amiii forward use case by hard-coding
# the input CUDS objects and passing them to the MoDS_Session class
# for execution.
def MOOonly_example(loadSurrogate="mods-sim-7131916930778391183"):
    logger.info("################  Start: MoDS MOO only Example ################")
    logger.info("Loading enviroment variables")
    load_dotenv()
    logger.info("Setting up the simulation inputs")

    moo_simulation = mods.MultiObjectiveSimulationOnly()
    moo_algorithm = mods.Algorithm(name="algorithm1", type="MOO", maxNumberOfResults=10, saveSurrogate=False, loadSurrogate=loadSurrogate)
    moo_algorithm.add(
        mods.Variable(name="var1", type="input"),
        mods.Variable(name="var2", type="input"),
        mods.Variable(name="var3", type="input"),
        mods.Variable(name="var4", type="output", objective="Maximise", minimum="0.5", weight="0.5"),
        mods.Variable(name="var5", type="output", objective="Minimise", maximum="1.5", weight="0.1"),
        mods.Variable(name="var6", type="output", objective="Maximise", minimum="2.5", weight="0.7"),
    )

    moo_simulation.add(moo_algorithm)
    
    pareto_front = None

    logger.info("Invoking the wrapper session")
    # Construct a wrapper and run a new session
    with ms.MoDS_Session() as session:
        wrapper = cuba.wrapper(session=session)
        wrapper.add(moo_simulation, rel=cuba.relationship)
        wrapper.session.run()

        pareto_front = search.find_cuds_objects_by_oclass(
            mods.ParetoFront, wrapper, rel=None
        )
        
        logger.info("Printing the simulation results.")
        
    if pareto_front:
            pretty_print(pareto_front[0])
                
    logger.info("################  End: MoDS MOO only Example ################")
    
    return pareto_front


if __name__ == "__main__":
    MOOonly_example()
