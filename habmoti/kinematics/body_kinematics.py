from dataclasses import dataclass
from enum import Enum, auto

import numpy as np


class JointCenter(Enum):
    LEFT_SHOULDER = auto()
    RIGHT_SHOULDER = auto()
    LEFT_ELBOW = auto()
    RIGHT_ELBOW = auto()
    LEFT_WRIST = auto()
    RIGHT_WRIST = auto()

    @staticmethod
    def from_joint_type(joint_type: int) -> "JointCenter":
        mapping = {
            0: JointCenter.LEFT_SHOULDER,
            1: JointCenter.RIGHT_SHOULDER,
            2: JointCenter.LEFT_ELBOW,
            3: JointCenter.RIGHT_ELBOW,
            4: JointCenter.LEFT_WRIST,
            5: JointCenter.RIGHT_WRIST,
        }
        return mapping.get(joint_type, None)


@dataclass(frozen=True)
class BodyKinematics:
    joint_centers: dict[JointCenter, np.ndarray]
