from scipy.signal import find_peaks

import numpy as np

from ....data.body_kinematics import BodyModel
from ....data.frame_data import FrameData

type JumpIndices = tuple[float, float, float]


def compute_jump_indices(body_model: BodyModel, frames: list[FrameData]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    data = np.array([data.body_kinematics.joint_centers for data in frames])
    left_foot_index = body_model.from_name("left_ankle")
    right_foot_index = body_model.from_name("right_ankle")

    mean_feet_height = np.mean(data[:, [left_foot_index, right_foot_index], 1], axis=1)
    mid_jump_indices, _ = find_peaks(mean_feet_height, height=0.1)

    # Find the valleys in between the first and last peaks of max_peaks to determine the landings/take-offs
    min_peaks, _ = find_peaks(-mean_feet_height, height=-0.1)
    min_peaks = [peak for peak in min_peaks if peak > mid_jump_indices[0] and peak < mid_jump_indices[-1]]
    start_jump_indices = min_peaks[:-1]
    end_jump_indices = min_peaks[1:]

    # Remove back the mid jumps which are not between a start and end jump
    mid_jump_indices = [
        mid
        for mid in mid_jump_indices
        if any(start < mid < end for start, end in zip(start_jump_indices, end_jump_indices))
    ]

    return [[start, mid, end] for start, mid, end in zip(start_jump_indices, mid_jump_indices, end_jump_indices)]
