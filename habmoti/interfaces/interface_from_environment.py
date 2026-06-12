import json
import os

from ..habmoti import Habmoti
from .utils import habmoti_from_dict


class InterfaceFromEnvironment:
    """
    Class representing the environment of an interface form.
    """

    def __init__(self) -> None:
        configuration = {"device": _fetch_device(), "analyzers": _fetch_analyzers()}
        self._habmoti = habmoti_from_dict(configuration)

    def exec(self) -> None:
        self._habmoti.initialize()
        self._habmoti.start_trial()
        self._habmoti.exec()

    @property
    def habmoti(self) -> Habmoti:
        return self._habmoti


def _fetch_device() -> dict:
    device_name = os.getenv("HABMOTI_DEVICE_TYPE")
    if device_name is None:
        raise ValueError("Environment variable 'HABMOTI_DEVICE_TYPE' is not set")

    if device_name == "zed":
        parameters = json.loads(os.getenv("HABMOTI_ZED_PARAMETERS", "{}"))
    elif device_name == "zed_mock":
        zed_parameters = json.loads(os.getenv("HABMOTI_ZED_PARAMETERS", "{}"))
        mock_parameters = json.loads(os.getenv("HABMOTI_ZED_MOCK_PARAMETERS", "{}"))
        parameters = mock_parameters | zed_parameters
    elif device_name == "csv_reader":
        parameters = json.loads(os.getenv("HABMOTI_CSV_READER_PARAMETERS", "{}"))
    else:
        raise NotImplementedError(f"Unsupported device type: {device_name}")
    return {"name": device_name, "parameters": parameters}


def _fetch_analyzers() -> list[dict]:
    analyzers = []
    for analyzer in json.loads(os.getenv("HABMOTI_ANALYZERS", "[]")):
        if analyzer == "to_console":
            parameters = json.loads(os.getenv("HABMOTI_TO_CONSOLE_ANALYZER_PARAMETERS", "{}"))
            if "joint_center" not in parameters:
                raise ValueError(
                    "Missing 'joint_center' parameter in the HABMOTI_TO_CONSOLE_ANALYZER_PARAMETERS environment variable"
                )
            analyzers.append({"name": analyzer, "parameters": parameters})
        elif analyzer == "to_csv":
            parameters = json.loads(os.getenv("HABMOTI_TO_CSV_ANALYZER_PARAMETERS", "{}"))
            if "filepath" not in parameters:
                raise ValueError(
                    "Missing 'filepath' parameter in the HABMOTI_TO_CSV_ANALYZER_PARAMETERS environment variable"
                )
            analyzers.append({"name": analyzer, "parameters": parameters})
        elif analyzer == "to_ogl":
            analyzers.append({"name": analyzer, "parameters": {}})
        elif analyzer == "to_matplotlib":
            analyzers.append({"name": analyzer, "parameters": {}})
        else:
            raise NotImplementedError(f"Unsupported analyzer type: {analyzer}")

    return analyzers
