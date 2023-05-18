import requests
import json
import urllib.parse
import time
from typing import Optional, Dict
import logging
import os

from .settings import MoDSWrapperSettings

logger = logging.getLogger(__name__)


class Agent_Bridge:
    """Class to handle communicating with the MoDSAgent servlet via a
    series of HTTP requests.
    """

    # # Polling interval when waiting or jobs to finish (seconds)
    # POLL_INTERVAL: int = 10

    # # Maximum number of requests when waiting for jobs to finish
    # MAX_ATTEMPTS: int = 60

    # # Additional URL part for job submission
    # SUBMISSION_URL_PART: str = "request?query="

    # # Additional URL part for requesting job outputs
    # OUTPUT_URL_PART: str = "output/request?query="

    # ID of generated job
    jobID: Optional[str] = None

    def __init__(self):
        self.settings = MoDSWrapperSettings()

    def runJob(self, jsonString: str) -> Optional[Dict]:
        """Runs a complete MoDS simulation on a remote machine via use of HTTP requests.
        Note that this method will block until the remote job is completed and has returned
        a result or error message.

        Arguments:
            jsonString -- JSON input data string

        Returns:
            Resulting JSON data objects (or None if error occurs)
        """
        logger.info("MoDS enpoint: %s", self.settings.agent_base_url)

        logger.info("Submitting job")
        submit_message = self.submitJob(jsonString)

        if submit_message is None:
            # TODO - How do we pass this error back to the calling SimPhoNY code?
            # TODO - Should there be a CUDS objects to hold error messages?
            logger.error("Job was not submitted successfully")
            return None

        if self.is_final_result(submit_message):
            return submit_message

        logger.info("Job successfully submitted.")

        # Wait a little time for the request to process
        time.sleep(self.settings.poll_intervall)

        # Request outputs
        outputs = self.requestOutputs()

        if (outputs is None):
            logger.error(
                "Could not get job outputs (failed job?), returning None")
            return None

        logger.info(
            "Job completed, returning JSON representation of output data")
        return outputs

    def submitJob(self, jsonString: str) -> dict:
        """Submits a job using a HTTP request with the input JSON string, stores
        resulting job ID returned by MoDS Agent.

        Arguments:
            jsonString (str) -- Input parameter data in raw JSON form

        Returns:
            True if a job was succesfully submitted
        """

        # Build the job submission URL
        url = self.buildSubmissionURL(jsonString)

        # Submit the request and get the response
        response = requests.get(url)

        # Check the HTTP return code
        if (response.status_code != 200):
            logger.error(
                "HTTP request returns unexpected status code %s", response.status_code)
            logger.error("Reason: %s", response.reason)
            return None

        # Get the returned RAW text
        returnedRaw = response.text

        # Parse into JSON
        returnedJSON = json.loads(returnedRaw)

        # Get the generated job ID from the JSON
        self.jobID = returnedJSON["jobID"]
        logger.info(
            "Job submitted successfully, resulting job ID is %s", self.jobID)
        return returnedJSON

    def is_final_result(self, submit_message) -> bool:
        if "jobID" in submit_message and "SimulationType" in submit_message and len(submit_message) > 2:
            logger.info("here!")
            return True
        else:
            return False

    def requestOutputs(self) -> Optional[Dict]:
        """Sends a HTTP request asking for the results of the submitted job.
        If the job fails, None is returned. Note that this function will block
        until the job has executed on the remote machine.

        Returns:
            JSON object detailing job outputs (None in case of failure)
        """

        # Build the URL
        url = self.buildOutputURL()

        # Submit the request
        result = self.__getJobResults(url, 1)
        if (result is None):
            logger.error("Job was not completed on the remote HPC!")
            return None

        # Detect if the job has actually finished successfully
        if ("message" in result):
            message = result["message"]

            if (message.find("error") >= 0):
                logger.error("Job finished with errors, no outputs received.")
                return None

        logger.info("Job finished successfully, output data received.")
        return result

    def buildSubmissionURL(self, jsonString: str) -> str:
        """Builds the submission URL for the input JSON string.

        Arguments:
            jsonString (str) -- Input parameter data in JSON form

        Returns:
            Full job submission URL
        """
        url = self.settings.agent_base_url + self.settings.submission_url_part
        url += self.encodeURL(jsonString)
        return url

    def buildOutputURL(self) -> str:
        """Builds the request outputs URL for the current job ID.

        Arguments:
            jsonString (str) -- Input parameter data in JSON form

        Returns:
            Full output request URL
        """
        url = self.settings.agent_base_url + self.settings.output_url_part

        # Build JSON from job ID
        jsonString = "{\"jobID\":\"" + str(self.jobID) + "\"}"

        url += self.encodeURL(jsonString)
        return url

    def encodeURL(self, string: str) -> str:
        """Encodes the input string into a valid URL

        Arguments:
            string (str) --- string to encode

        Returns:
            Valid URL
        """
        return urllib.parse.quote(string)

    def __getJobResults(self, url: str, attempt: int) -> Optional[Dict]:
        """Make a HTTP request to get the final results of the submitted job.
        Recurses until the request reports that the job is finished (or a
        maximum number of attempts is reached)

        Arguments:
            url (str)     -- Output request URL
            attempt (int) -- Current attempt index

        Returns:
            JSON object parsed from response (or None if failure occurs)
        """

        # Fail at is more than max attempts
        if (attempt >= self.settings.max_attemps):
            logger.warning(
                "Maximum number of attempts reached, considering job a failure.")
            return None

        # Submit the request
        response = requests.get(url)

        # Check the HTTP return code
        if (response.status_code == 204):
            logger.info("Job still running (attempt %s of %s)",
                        attempt, self.settings.max_attemps)
            time.sleep(self.settings.poll_intervall)
            return self.__getJobResults(url, attempt + 1)
        elif (response.status_code != 200):
            logger.error(
                "HTTP request returns unexpected status code %s", response.status_code)
            logger.error("Reason: %s", response.reason)
            return None
        else:
            # Get the returned RAW text
            returnedRaw = response.text

            # Parse into JSON
            returnedJSON = json.loads(returnedRaw)

            return returnedJSON
