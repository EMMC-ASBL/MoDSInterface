import osp.core.utils.simple_search as search
import osp.wrappers.sim_cmcl_mods_wrapper.agent_cases as ac
from typing import Any, List
from osp.core.cuds import Cuds
from osp.core.namespaces import mods, cuba
import json
import logging
from typing import Dict

logger = logging.getLogger(__name__)

INPUTS_KEY = "Inputs"
OUTPUTS_KEY = "Outputs"
SETTINGS_KEY = "Settings"
SIM_TYPE_KEY = "SimulationType"

class CUDS_Adaptor:
    """Class to handle translation between CUDS and JSON objects."""

    @staticmethod
    def toJSON(root_cuds_object: Cuds, simulation_template: ac.SimCaseTemplate) -> str:
        """Translates the input CUDS object to a JSON object matching the
        INPUT format of the remote MoDS simulation."""

        # NOTE - This translation relies heavily on the structure of the CUDS data,
        # which is defined by the ontology. If the ontology changes, it is likely
        # that this translation will need updating too. The translation is defined
        # in the agent_cases module.

        jsonData = {}
        jsonData[SIM_TYPE_KEY] = simulation_template.template
        jsonData[SETTINGS_KEY] = []
        jsonData[INPUTS_KEY] = []

        dataPoints: List[Cuds] = search.find_cuds_objects_by_oclass(
         simulation_template.caseInputTopEntity, root_cuds_object, rel=None
        )  # type: ignore

        settings: List[Cuds] = search.find_cuds_objects_by_oclass(
         simulation_template.caseSettingsTopEntity, root_cuds_object, rel=None
        )  # type: ignore

        logger.info("Registering simulation settings")
        CUDS_Adaptor.inputCUDStoJSON(jsonData[SETTINGS_KEY], simulation_template.settings, settings)
        logger.info("All settings successfully registered.")

        # Find and register all input quantities (input)
        logger.info("Registering inputs")
        CUDS_Adaptor.inputCUDStoJSON(jsonData[INPUTS_KEY], simulation_template.inputs, dataPoints)
        logger.info("All inputs successfully registered.")

        jsonDataStr = json.dumps(jsonData)
        return jsonDataStr

    @staticmethod
    def inputCUDStoJSON(jsonData, semEntities, dataPoints):
        inputs_ = {}
        for semEntity in semEntities:
            for datum in dataPoints:
                datum_items = datum.get(oclass=semEntity)
                if not datum_items: return

                for item in datum_items:
                    if item.name not in inputs_:
                        inputs_[item.name] = {
                            "values": [item.value],
                            "name": item.name
                        }
                    else:
                        input_values_ = inputs_[item.name]["values"]
                        input_values_.append(item.value)
                        inputs_[item.name]["values"] = input_values_

        jsonData.extend(inputs_.values())

    @staticmethod
    def toCUDS(
        root_cuds_object, jsonResults: Dict, simulation_template: ac.SimCaseTemplate
    ) -> None:
        """Writes JSON output of an engine simulation into CUDS."""

        logger.info("Converting JSON output to CUDS")
        if not jsonResults:
            logger.warning("Empty JSON output. Nothing to convert.")
            return

        if simulation_template.template == 'MOO':
            logger.info("Registering outputs")

            moo_simulation = root_cuds_object.get(oclass=mods.MultiObjectiveSimulation, rel=cuba.relationship)[0]
            ParetoFront = mods.ParetoFront()

            num_values = len(jsonResults[OUTPUTS_KEY][0]["values"])
            for i in range(num_values):
                data_point = mods.DataPoint()
                for output in jsonResults[OUTPUTS_KEY]:
                    out_value = output["values"][i]
                    out_name = output["name"]

                    data_point.add(
                        mods.DataPointItem(name=out_name, value=out_value),
                        rel=mods.hasPart,
                    )

                ParetoFront.add(data_point)

            moo_simulation.add(ParetoFront)
            logger.info("All outputs successfully registered.")
