import hdmr
import moo_only
import osp.core.utils.simple_search as search
from osp.core.namespaces import mods


def HDMR_and_MOO_example():
    job_id = hdmr.HDMR_example()
    job_id_item = search.find_cuds_objects_by_oclass(
        mods.JobIDItem, job_id[0], rel=None
    )
    moo_only.MOOonly_example(surrogateToLoad=job_id_item[0].name)


if __name__ == "__main__":
    HDMR_and_MOO_example()
