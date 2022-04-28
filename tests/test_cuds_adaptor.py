import logging
import json
from osp.core.cuds import Cuds
import osp.wrappers.sim_cmcl_mods_wrapper.cuds_adaptor as cuds_adaptor
import osp.wrappers.sim_cmcl_mods_wrapper.engine_sim_templates as engtempl
import os
import pytest
from pytest_lazyfixture import lazy_fixture


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
MOO_REF_JSON = os.path.join(THIS_DIR, "moo.json_ref")
MOO_ANALYTIC_REF_JSON = os.path.join(THIS_DIR, "moo_analytic.json_ref")

# Set the level of the logger in OSP Core
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@pytest.mark.parametrize(
    "cuds, ref_data_path",
    [
        (lazy_fixture("moo_data"), MOO_REF_JSON),
        (lazy_fixture("moo_analytic_data"), MOO_ANALYTIC_REF_JSON),
    ]
)
def test_cuds_adaptor(cuds: Cuds, ref_data_path: str):
    print('start')
    json_data_str = cuds_adaptor.CUDS_Adaptor.toJSON(
        root_cuds_object = cuds,
        simulation_template=engtempl.Engine_Template.MOO)

    json_data_dict = json.loads(json_data_str)
    json_ref_data_dict = json.load(open(ref_data_path, 'r'))

    # uncomment to regenerate the ref results
    #json.dump(json_data_dict, open(ref_data_path, 'w'), indent=4)

    assert json_data_dict == json_ref_data_dict
