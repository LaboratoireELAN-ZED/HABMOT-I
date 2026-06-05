from dataclasses import dataclass, field

from ..analyses.analysis import Analysis
from ..kinematics.body_kinematics import BodyKinematics


@dataclass(frozen=True)
class FrameData:
    timestamp: float
    body_kinematics: BodyKinematics
    analysis: Analysis = field(default_factory=Analysis)

    def serialize(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "body_kinematics": {
                joint.name: self.body_kinematics.joint_centers[joint] for joint in self.body_kinematics.joint_centers
            },
            "analysis": self.analysis.current,
        }
