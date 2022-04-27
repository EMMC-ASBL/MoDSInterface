import logging
from flask import Blueprint, request
import json
import uuid

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Blueprint Configuration
mods_mock_agent_bp = Blueprint("mods_mock_agent_bp", __name__)

JOB_INPUTS = {}


# Show an instructional message at the app root
@mods_mock_agent_bp.route("/request", methods=["GET"])
def runSimulation():
    # logger.info(request.args)
    query = json.loads(request.args["query"])
    inputs = query["Inputs"]

    outputs = {}
    outputs["Outputs"] = []
    outputs["Outputs"].extend(
        [
            {"name": inputs[0]["name"], "values": [2]*10},
            {"name": inputs[1]["name"], "values": [1]*10},
            {"name": inputs[2]["name"], "values": [5]*10},
            {"name": inputs[3]["name"], "values": [7]*10},
            {"name": inputs[4]["name"], "values": [1]*10},
            {"name": inputs[5]["name"], "values": [0.1]*10}
        ]
    )
    jobId = str(uuid.uuid4())
    JOB_INPUTS[jobId] = outputs
    return {"jobID": jobId}, 200


# Show an instructional message at the app root
@mods_mock_agent_bp.route("/output/request", methods=["GET"])
def getOutputs():
    # logger.info(request.args)
    query = json.loads(request.args["query"])
    jobId = query["jobID"]
    outputs = {}
    try:
        outputs = JOB_INPUTS[jobId]
    except LookupError:
        logger.error("Incorrect jobId.")
        return outputs, 400
    return outputs, 200
