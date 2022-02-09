import osp.core.utils.simple_search as search
from typing import Any, List
import osp.wrappers.sim_cmcl_mods_wrapper.engine_sim_templates as engtempl
from osp.core.cuds import Cuds
from osp.core.namespaces import mods, cuba
import json
import logging
from typing import Dict
from enum import Enum

logger = logging.getLogger(__name__)

INPUTS_KEY = "Inputs"
OUTPUTS_KEY = "Outputs"
SETTINGS_KEY = "Settings"
SIM_TYPE_KEY = "SimulationType"

class CUDS_Adaptor:
    """Class to handle translation between CUDS and JSON objects."""

    @staticmethod
    def toJSON(root_cuds_object: Cuds, simulation_template: Enum) -> str:
        """Translates the input CUDS object to a JSON object matching the
        INPUT format of the remote MoDS simulation."""

        # NOTE - This translation relies heavily on the structure of the CUDS data,
        # which is defined by the ontology. If the ontology changes, it is likely
        # that this translation will need updating too. The translation is defined
        # in the agent_cases module.

        jsonData = {}
        jsonData[SIM_TYPE_KEY] = simulation_template.name
        jsonData[SETTINGS_KEY] = []
        jsonData[INPUTS_KEY] = []


        settings: List[Cuds] = search.find_cuds_objects_by_oclass(
         mods.Settings, root_cuds_object, rel=None
        )  # type: ignore

        dataPoints: List[Cuds] = search.find_cuds_objects_by_oclass(
         mods.DataPoint, root_cuds_object, rel=None
        )  # type: ignore

        analyticModels: List[Cuds] = search.find_cuds_objects_by_oclass(
         mods.AnalyticModel, root_cuds_object, rel=None
        )  # type: ignore

        logger.info("Registering simulation settings.")
        if settings:
            CUDS_Adaptor.inputCUDStoJSON(
                jsonData = jsonData[SETTINGS_KEY],
                semEntity = mods.SettingItem,
                dataPoints = settings,
                semIdentifier ='name',
                semAttrToSynMap = [{'semName': 'name', 'synName': 'name', 'synType': str},
                {'semName': 'value', 'synName': 'values', 'synType': list}])
            logger.info("All settings successfully registered.")
        else:
            logger.info("Simulation settings not found.")

        logger.info("Registering data inputs.")
        if dataPoints:
            # Find and register all input quantities (input)
            CUDS_Adaptor.inputCUDStoJSON(
                jsonData = jsonData[INPUTS_KEY],
                semEntity = mods.DataPointItem,
                dataPoints = dataPoints,
                semIdentifier ='name',
                semAttrToSynMap = [{'semName': 'name', 'synName': 'name', 'synType': str},
                {'semName': 'value', 'synName': 'values', 'synType': list}])

            logger.info("All inputs successfully registered.")
        else:
            logger.info("Simulation inputs not found.")

        logger.info("Registering analytic model inputs.")
        if analyticModels:
            CUDS_Adaptor.inputCUDStoJSON(
                jsonData = jsonData[INPUTS_KEY],
                semEntity = mods.Function,
                dataPoints = analyticModels,
                semIdentifier ='name',
                semAttrToSynMap = [{'semName': 'name', 'synName': 'name', 'synType': str},
                {'semName': 'formula', 'synName': 'formula', 'synType': str}])
            logger.info("All analytic models successfully registered.")
        else:
            logger.info("Simulation analytic model inputs not found.")

        jsonDataStr = json.dumps(jsonData)
        return jsonDataStr

    @staticmethod
    def inputCUDStoJSON(jsonData, semEntity, dataPoints, semIdentifier, semAttrToSynMap):
        inputs_ = {}
        for datum in dataPoints:
            datum_items = datum.get(oclass=semEntity)
            if not datum_items: return

            for item in datum_items:
                item_id = getattr(item, semIdentifier)
                if item_id not in inputs_:
                    inputs_[item_id] = {}
                    for sem_syn in semAttrToSynMap:
                        semName = sem_syn['semName']
                        synName = sem_syn['synName']
                        synType = sem_syn['synType']

                        semValue = getattr(item, semName)
                        inputs_[item_id][synName] = [semValue] if synType is list else semValue
                else:
                    for sem_syn in semAttrToSynMap:
                        semName = sem_syn['semName']
                        synName = sem_syn['synName']
                        synType = sem_syn['synType']

                        semValue = getattr(item, semName)
                        if synType is list:
                            input_values_ = inputs_[item_id][synName]
                            input_values_.append(semValue)
                            inputs_[item_id][synName] = input_values_

        jsonData.extend(inputs_.values())

    @staticmethod
    def toCUDS(
        root_cuds_object, jsonResults: Dict, simulation_template: Enum
    ) -> None:
        """Writes JSON output of an engine simulation into CUDS."""

        logger.info("Converting JSON output to CUDS")
        if not jsonResults:
            logger.warning("Empty JSON output. Nothing to convert.")
            return

        if simulation_template == engtempl.Engine_Template.MOO:
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
