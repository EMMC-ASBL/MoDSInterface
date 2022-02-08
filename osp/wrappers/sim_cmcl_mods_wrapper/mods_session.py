from osp.core.session import SimWrapperSession
from osp.wrappers.sim_cmcl_mods_wrapper.mods_engine import MoDS_Engine
from osp.wrappers.sim_cmcl_mods_wrapper import Agent_Bridge
from osp.core.cuds import Cuds
import logging

logger = logging.getLogger(__name__)


class MoDS_Session(SimWrapperSession):
    """This session class wraps a MoDS_Engine instance, calls it, then passes the
    JSON data it has produced to an Agent_Bridge instance that runs the remote
    simulation with the MoDS Suite."""

    def __init__(self, engine=None, **kwargs):
        """Initialises the session and creates a new MoDS_Engine instance.

        Arguments:
            engine -- MoDS_Engine instance
            kwargs -- Keyword arguments
        """

        if engine is None:
            engine = MoDS_Engine()
        logger.info(f"Initialise MoDS_Session with the {engine.name} engine")
        super().__init__(engine, **kwargs)

    def __str__(self):
        """Returns a textual representation."""
        return "MoDS Wrapper Session"

    def _run(self, root_cuds_object: Cuds):
        """Runs the Agent_Bridge class to execute a remote MoDS simulation.

        Note that once CUDS data is passed into this method, it should be
        considered READ-ONLY by any calling code outside this wrapper.

        Arguments:
            root_cuds_object -- Root CUDS object representing input data
        """
        logger.info("===== Start: MoDS_Session =====")

        # Determine template from root CUDS object
        self._engine.determineTemplate(root_cuds_object)

        # Use the engine to generate JSON inputs
        jsonSimCase = self._engine.generateJSON(root_cuds_object)
        # Run remote simulation (via Agent_Bridge)
        agentBridge = Agent_Bridge()
        jsonResults = agentBridge.runJob(jsonSimCase)

        # Pass results (in JSON form) back to the engine for parsing
        # this writes the results back to CUDS
        self._engine.parseResults(root_cuds_object, jsonResults)

        logger.info("===== End: MoDS_Session =====")

    def _apply_added(self, root_obj, buffer):
        """Not used in the this concrete wrapper.

        Args:
            root_obj (Cuds): The wrapper cuds object
            buffer (Dict[UUID, Cuds]): All Cuds objects that have been added
        """
        pass

    def _apply_updated(self, root_obj, buffer):
        """Not used in the this concrete wrapper.

        Args:
            root_obj (Cuds): The wrapper cuds object
            buffer (Dict[UUID, Cuds]): All Cuds objects that have been updated
        """
        pass

    def _apply_deleted(self, root_obj, buffer):
        """Not used in the this concrete wrapper.

        Args:
            root_obj (Cuds): The wrapper cuds object.
            buffer (Dict[UUID, Cuds]): All Cuds objects that have been deleted
        """
        pass

    def _load_from_backend(self, uids, expired=None):
        """Not used in the this concrete wrapper.

        :param uids: List of uids to load
        :type uids: List[UUID]
        :param expired: Which of the cuds_objects are expired.
        :type expired: Set[UUID]
        """
        for uid in uids:
            if uid in self._registry:
                yield self._registry.get(uid)
            else:
                yield None
