import logging
from flask import Blueprint, request
import json
import uuid

ERROR_MESSAGE = "Incorrect simulation inputs."
PRIMARY_ALGORITHMS = {"MOOonly": "MOO", "MOO": "MOO", "HDMR": "GenSurrogateAlg",
                      "Sensitivity": "GenSurrogateAlg", "Evaluate": "SamplingAlg", "MCDM": "MCDM"}

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Blueprint Configuration
mods_mock_agent_bp = Blueprint("mods_mock_agent_bp", __name__)

JOB_INPUTS = {}


# Show an instructional message at the app root
@mods_mock_agent_bp.route("/request", methods=["GET"])
def run_simulation():
    # logger.info(request.args)
    query = json.loads(request.args["query"])

    jobID = str(uuid.uuid4())

    simulation_type = query["SimulationType"]

    print("SimulationType: " + simulation_type)

    status = {"jobID": jobID, "SimulationType": simulation_type}
    outputs = status.copy()

    primary_algorithm = get_primary_algorithm(query)

    output_variables = [variable["name"]
                        for variable in primary_algorithm["variables"] if variable["type"] == "output"]
    input_variables = [variable["name"]
                       for variable in primary_algorithm["variables"] if variable["type"] == "input"]
    variables = input_variables + output_variables

    if simulation_type == "Evaluate":
        inputs = query["Inputs"]
        try:
            inputs_num = len(inputs[0]["values"])
        except LookupError:
            logger.error(ERROR_MESSAGE)
            return ERROR_MESSAGE, 400

        output_variables = [variable["name"] for variable in query["Algorithms"]
                            [1]["variables"] if variable["type"] == "output"]

        outputs["Outputs"] = query["Inputs"].copy()

        outputs["Outputs"].extend(
            [
                {"name": output_variable, "values": [
                    float(i) for i in range(inputs_num)]}
                for output_variable in output_variables
            ]
        )
    elif simulation_type == "MOOonly" or simulation_type == "MOO" or simulation_type == "MCDM":

        max_number_of_results = int(primary_algorithm["maxNumberOfResults"])

        outputs["Outputs"] = []

        outputs["Outputs"].extend(
            [{"name": variable, "values": [float(i) for i in range(
                max_number_of_results)]} for variable in variables]
        )
        if simulation_type == "MCDM":
            status["Outputs"] = outputs["Outputs"]
    elif simulation_type == "HDMR":
        pass
    elif simulation_type == "Sensitivity":
        input_variable_number = len(input_variables)
        sensitivity_label_order_one = {"order": 1, "values": input_variables}
        sensitivity_label_order_two = {"order": 2, "values": [
            input_variables[i] + " and " + input_variables[j]
            for i in range(0, input_variable_number)
            for j in range(i+1, input_variable_number)]}
        sensitivity_labels = [
            sensitivity_label_order_one, sensitivity_label_order_two]

        outputs["Sensitivities"] = [{"name": output_variable,
                                     "labels": sensitivity_labels,
                                     "values": [
                                         {"order": 1, "values": [
                                             float(i) for i in range(len(sensitivity_label_order_one["values"]))]},
                                         {"order": 2, "values": [
                                             float(i) for i in range(len(sensitivity_label_order_two["values"]))]}
                                     ]} for output_variable in output_variables]
        status["Sensitivities"] = outputs["Sensitivities"]
    else:
        logger.error(ERROR_MESSAGE)
        return ERROR_MESSAGE, 400

    JOB_INPUTS[jobID] = outputs
    return status, 200


def get_primary_algorithm(query: dict) -> dict:
    return [algorithm for algorithm in query["Algorithms"]
            if algorithm["type"] == PRIMARY_ALGORITHMS[query["SimulationType"]]][0]


# Show an instructional message at the app root
@mods_mock_agent_bp.route("/output/request", methods=["GET"])
def getOutputs():
    # logger.info(request.args)
    query = json.loads(request.args["query"])
    jobID = query["jobID"]
    outputs = {}
    try:
        outputs = JOB_INPUTS[jobID]
    except LookupError:
        logger.error(ERROR_MESSAGE)
        return outputs, 400
    return outputs, 200
