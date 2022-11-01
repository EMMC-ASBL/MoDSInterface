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
def evaluate_example(SurrogateToLoad="mods-sim-6309672575118509368"):
    logger.info("################  Start: MoDS MOO only Example ################")
    logger.info("Loading enviroment variables")
    load_dotenv()
    logger.info("Setting up the simulation inputs")

    evaluate_simulation = mods.EvaluateSurrogate(SurrogateToLoad=SurrogateToLoad)
    evaluate_algorithm = mods.Algorithm(name="algorithm1", type="SamplingAlg")
    evaluate_algorithm.add(
        mods.Variable(name="var1", type="input"),
        mods.Variable(name="var2", type="input"),
        mods.Variable(name="var3", type="input"),
        mods.Variable(name="var4", type="output"),
        mods.Variable(name="var5", type="output"),
        mods.Variable(name="var6", type="output"),
    )

    evaluate_simulation.add(evaluate_algorithm)

    example_data = [
        ["var1", "var2", "var3"],
        [0.15, 0.45, 0.55],
        [0.35, 0.85, 0.15],
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

    evaluate_simulation.add(input_data)
    
    ouput_data = None

    logger.info("Invoking the wrapper session")
    # Construct a wrapper and run a new session
    with ms.MoDS_Session() as session:
        wrapper = cuba.wrapper(session=session)
        wrapper.add(evaluate_simulation, rel=cuba.relationship)
        wrapper.session.run()

        ouput_data = search.find_cuds_objects_by_oclass(
            mods.OutputData, wrapper, rel=None
        )
        job_id = search.find_cuds_objects_by_oclass(
            mods.JobID, wrapper, rel=None
        )
        
        logger.info("Printing the simulation results.")
        
        if ouput_data:
            pretty_print(ouput_data[0])
        if job_id:
            pretty_print(job_id[0])
                
    logger.info("################  End: MoDS MOO only Example ################")
    
    return ouput_data


if __name__ == "__main__":
    evaluate_example()
