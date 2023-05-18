import logging
from osp.core.namespaces import mods, cuba
import osp.core.utils.simple_search as search
import pytest
import osp.wrappers.sim_cmcl_mods_wrapper.mods_session as ms

# Set the level of the logger in OSP Core
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def test_moo(moo_data):
    logger.info("################  Start: MoDS MOO Example ################")

    logger.info("Invoking the wrapper session")
    # Construct a wrapper and run a new session
    with ms.MoDS_Session() as session:
        wrapper = cuba.wrapper(session=session)
        wrapper.add(moo_data, rel=cuba.relationship)
        wrapper.session.run()

        pareto_front = search.find_cuds_objects_by_oclass(
            mods.ParetoFront, wrapper, rel=None
        )

        assert pareto_front is not None
        assert len(pareto_front[0].get(oclass=mods.DataPoint)) == 10


@pytest.mark.skip(reason="analytic data is not currently supported")
def test_moo_analytic(moo_analytic_data):
    logger.info("################  Start: MoDS MOO Analytic Example ################")

    logger.info("Invoking the wrapper session")
    # Construct a wrapper and run a new session
    with ms.MoDS_Session() as session:
        wrapper = cuba.wrapper(session=session)
        wrapper.add(moo_analytic_data, rel=cuba.relationship)
        wrapper.session.run()

        pareto_front = search.find_cuds_objects_by_oclass(
            mods.ParetoFront, wrapper, rel=None
        )

        assert pareto_front is not None
        assert len(pareto_front[0].get(oclass=mods.DataPoint)) == 10
