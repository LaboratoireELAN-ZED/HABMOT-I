from datetime import datetime
from typing import override, TYPE_CHECKING

from ..analyzer import Analyzer

if TYPE_CHECKING:
    from ...data.body_kinematics import BodyModel
    from ...habmoti import Habmoti, FrameData


class ToConsoleAnalyzer(Analyzer):
    def __init__(self, joint_center: BodyModel):
        self._joint_center = joint_center

        super().__init__()

    @property
    @override
    def name(self) -> str:
        return f"Console Viewer ({self._joint_center.name})"

    @override
    def initialize(self, habmoti: Habmoti) -> None:
        pass

    @override
    def perform(self, frame_data: FrameData) -> None:
        timestamp = datetime.fromtimestamp(frame_data.timestamp / 1000.0)
        print(f"At {timestamp}, received: {frame_data.body_kinematics.joint_centers[self._joint_center]}")

    @override
    def dispose(self) -> None:
        pass
