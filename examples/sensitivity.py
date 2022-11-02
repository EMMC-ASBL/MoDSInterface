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
def sensitivit_example(SurrogateToLoad="mods-sim-6309672575118509368"):
    logger.info("################  Start: MoDS MOO only Example ################")
    logger.info("Loading enviroment variables")
    load_dotenv()
    logger.info("Setting up the simulation inputs")

    sensitivity_simulation = mods.SensitivityAnalysis(SurrogateToLoad=SurrogateToLoad, SaveSurrogate=False)
    sensitivitye_algorithm = mods.Algorithm(name="algorithm1", type="GenSurrogateAlg")
    sensitivitye_algorithm.add(
        mods.Variable(name="var1", type="input"),
        mods.Variable(name="var2", type="input"),
        mods.Variable(name="var3", type="input"),
        mods.Variable(name="var4", type="output"),
        mods.Variable(name="var5", type="output"),
        mods.Variable(name="var6", type="output"),
    )

    sensitivity_simulation.add(sensitivitye_algorithm)
    
    sensitivities = None

    logger.info("Invoking the wrapper session")
    # Construct a wrapper and run a new session
    with ms.MoDS_Session() as session:
        wrapper = cuba.wrapper(session=session)
        wrapper.add(sensitivity_simulation, rel=cuba.relationship)
        wrapper.session.run()

        sensitivities = search.find_cuds_objects_by_oclass(
            mods.SensitivityDataSet, wrapper, rel=None
        )
        job_id = search.find_cuds_objects_by_oclass(
            mods.JobID, wrapper, rel=None
        )
        
        logger.info("Printing the simulation results.")
        
        if sensitivities:
            pretty_print(sensitivities[0])
        if job_id:
            pretty_print(job_id[0])
                
    logger.info("################  End: MoDS MOO only Example ################")
    
    return sensitivities


if __name__ == "__main__":
    sensitivit_example()
