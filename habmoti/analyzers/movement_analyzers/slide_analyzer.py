from dataclasses import dataclass
import logging
from typing import override

import numpy as np
import numpy.typing as npt

from .utils.body_model_utils import joint_angle
from .utils.jump_utils import JumpIndices, compute_jump_indices
from .data_movement_analyzer import DataMovementAnalyzer, Axes

_logger = logging.getLogger(__name__)


@dataclass
class HabmotCriteriaSlide:
    leading_foot_is_off_ground: bool = False

    def __str__(self) -> str:
        return f"""#####################
Slide analysis results:
  2. Leading foot is off the ground: {self.leading_foot_is_off_ground}
#####################"""


class SlideAnalyzer(DataMovementAnalyzer):
    def __init__(self, show_debug_graphs: bool = False) -> None:
        super().__init__()
        self._criteria: HabmotCriteriaSlide | None = None
        self._show_debug_graphs = show_debug_graphs

    @property
    @override
    def name(self) -> str:
        return "Slide"

    @override
    def start_trial(self) -> None:
        self._criteria = HabmotCriteriaSlide()
        super().start_trial()

    @override
    def stop_trial(self) -> None:
        super().stop_trial()
        self._perform_post_trial_analysis()

    @override
    def _perform_post_trial_analysis(self) -> None:
        # Find the peaks in the mean feet y position to find the mid-jump frames
        jump_indices = compute_jump_indices(
            body_model=self._habmoti.device.body_model, frames=self._data_centered, threshold=0.05
        )
        leading_foot = self._compute_leading_foot(jump_indices)

        # Proceed to the analyses
        is_success = self._compute_is_leading_foot_off_ground(jump_indices, leading_foot)
        self._criteria.leading_foot_is_off_ground = is_success

        # Print the results to the console
        _logger.info(f"\n{self._criteria}")

        if self._show_debug_graphs:
            self._show_data(blocking=False, jump_indices=jump_indices)

    @override
    def dispose(self) -> None:
        self._criteria = None
        super().dispose()

    def _compute_leading_foot(self, jump_indices: tuple[JumpIndices]) -> list[str]:
        # The leading foot is the furthest of the body line at the peak of the jump
        joint_centers = np.array([data.body_kinematics.joint_centers for data in self._data_centered])
        mid_jump = [jump[1] for jump in jump_indices]

        index_of = lambda name: self._habmoti.device.body_model.from_name(name)
        left_foot = joint_centers[mid_jump, index_of("left_ankle"), Axes.SAGITTAL.value]
        right_foot = joint_centers[mid_jump, index_of("right_ankle"), Axes.SAGITTAL.value]

        return ["left" if value else "right" for value in np.abs(left_foot) > np.abs(right_foot)]

    def _compute_is_leading_foot_off_ground(self, jump_indices: tuple[JumpIndices], leading_foot: list[str]) -> bool:
        joint_centers = np.array([data.body_kinematics.joint_centers for data in self._data_centered])
        mid_jump = [jump[1] for jump in jump_indices]

        index_of = lambda name: self._habmoti.device.body_model.from_name(name)
        left_foot_height = joint_centers[mid_jump, index_of("left_ankle"), Axes.VERTICAL.value]
        right_foot_height = joint_centers[mid_jump, index_of("right_ankle"), Axes.VERTICAL.value]

        threshold = 0.05  # 5 cm off the ground is considered off the ground
        foot_is_off_ground = []
        for foot, left_height, right_height in zip(leading_foot, left_foot_height, right_foot_height):
            if foot == "left":
                foot_is_off_ground.append(left_height > threshold)
            elif foot == "right":
                foot_is_off_ground.append(right_height > threshold)
            else:
                raise ValueError(f"Unexpected foot value: {foot}")

        return all(foot_is_off_ground)

    def _show_data(self, blocking: bool, jump_indices: tuple[JumpIndices]) -> None:
        from matplotlib import pyplot as plt

        t0 = self._data_centered[0].timestamp if self._data_centered else 0
        t = np.array([data.timestamp - t0 for data in self._data_centered]) / 1000.0

        axis_index = Axes.VERTICAL.value
        joint_centers = np.array([data.body_kinematics.joint_centers for data in self._data_centered])
        left_foot_height = joint_centers[:, self._habmoti.device.body_model.from_name("left_ankle"), axis_index]
        right_foot_height = joint_centers[:, self._habmoti.device.body_model.from_name("right_ankle"), axis_index]
        mean_feet_height = (left_foot_height + right_foot_height) / 2

        mid_jump_indices = [jump[1] for jump in jump_indices]

        fig = plt.figure("Slide Analysis")
        plt.plot(t, left_foot_height, label="Left Foot Y")
        plt.plot(t, right_foot_height, label="Right Foot Y")
        plt.plot(t, mean_feet_height, label="Mean Feet Y", linestyle="--")
        [plt.axvline(x=t[index], color="g") for index in mid_jump_indices]
        plt.legend()

        plt.title("Slide Analysis")
        plt.xlabel("Time (s)")
        plt.ylabel("Height Position")
        plt.pause(0.1)

        # Plot a vertical line a index to show where we are in the data
        line = plt.axvline(x=0, color="r", linestyle="--")
        super()._show_data(blocking=blocking, fig=fig, t=t, line=line)

    def _update_extra_show_data(self, index: int, fig, t: np.ndarray, line) -> bool:
        from matplotlib import pyplot as plt

        if not plt.fignum_exists(fig.number):
            return False

        x = t[index]
        line.set_xdata([x, x])

        plt.pause((t[index] - t[index - 1]) if index > 0 else 1.0)
        return True
