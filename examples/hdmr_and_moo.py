import hdmr
import moo_only
import osp.core.utils.simple_search as search
from osp.core.namespaces import mods

def HDMR_and_MOO_example():
    pareto_front = hdmr.HDMR_example()
    job_id = search.find_cuds_objects_by_oclass(
                mods.JobIDItem, pareto_front[0], rel=None
            )
    moo_only.MOOonly_example(job_id[0].name)

if __name__ == "__main__":
    HDMR_and_MOO_example()
    
