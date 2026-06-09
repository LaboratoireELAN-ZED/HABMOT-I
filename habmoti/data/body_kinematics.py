from dataclasses import dataclass
from enum import IntEnum
from typing import Generic, TypeVar, override

import numpy as np
from numpy.typing import NDArray


class BodyModel(IntEnum):
    @property
    def label(self) -> str:
        return self.name.lower()

    @staticmethod
    def from_name(name: str) -> "BodyModel":
        raise NotImplementedError("This method should be implemented in subclasses of BodyModel")

    @staticmethod
    def segment_links(self) -> list[tuple["BodyModel", "BodyModel"]]:
        raise NotImplementedError("This method should be implemented in subclasses of BodyModel")


class BodyModel18Joints(BodyModel):
    NOSE = 0
    RIGHT_KNEE = 9
    NECK = 1
    RIGHT_ANKLE = 10
    RIGHT_SHOULDER = 2
    LEFT_HIP = 11
    RIGHT_ELBOW = 3
    LEFT_KNEE = 12
    RIGHT_WRIST = 4
    LEFT_ANKLE = 13
    LEFT_SHOULDER = 5
    RIGHT_EYE = 14
    LEFT_ELBOW = 6
    LEFT_EYE = 15
    LEFT_WRIST = 7
    RIGHT_EAR = 16
    RIGHT_HIP = 8
    LEFT_EAR = 17

    @staticmethod
    def from_name(name: str) -> "BodyModel":
        return BodyModel18Joints[name.upper()]

    @staticmethod
    def segment_links() -> list[tuple["BodyModel", "BodyModel"]]:
        # Define the segment links for the 18-joint model
        return [
            (BodyModel18Joints.NOSE, BodyModel18Joints.NECK),
            (BodyModel18Joints.NECK, BodyModel18Joints.RIGHT_SHOULDER),
            (BodyModel18Joints.NECK, BodyModel18Joints.LEFT_SHOULDER),
            (BodyModel18Joints.RIGHT_SHOULDER, BodyModel18Joints.RIGHT_ELBOW),
            (BodyModel18Joints.LEFT_SHOULDER, BodyModel18Joints.LEFT_ELBOW),
            (BodyModel18Joints.RIGHT_ELBOW, BodyModel18Joints.RIGHT_WRIST),
            (BodyModel18Joints.LEFT_ELBOW, BodyModel18Joints.LEFT_WRIST),
            (BodyModel18Joints.NECK, BodyModel18Joints.RIGHT_HIP),
            (BodyModel18Joints.NECK, BodyModel18Joints.LEFT_HIP),
            (BodyModel18Joints.RIGHT_HIP, BodyModel18Joints.RIGHT_KNEE),
            (BodyModel18Joints.LEFT_HIP, BodyModel18Joints.LEFT_KNEE),
            (BodyModel18Joints.RIGHT_KNEE, BodyModel18Joints.RIGHT_ANKLE),
            (BodyModel18Joints.LEFT_KNEE, BodyModel18Joints.LEFT_ANKLE),
        ]


BodyModelType = TypeVar("BodyModelType", bound=BodyModel)


@dataclass(frozen=True)
class BodyKinematics(Generic[BodyModelType]):
    body_model: type[BodyModelType]
    values: NDArray[np.float64]

    def __post_init__(self) -> None:
        if self.values.ndim != 2 or self.values.shape[1] != 3:
            raise ValueError("Expected shape (n_joints, 3)")

    @property
    def joint_centers(self) -> NDArray[np.float64]:
        return self.values

    @property
    def body_list(self) -> list[NDArray[np.float64]]:
        return [self.values]


@dataclass(frozen=True)
class MultiBodyKinematics(BodyKinematics[BodyModelType]):
    body_model: type[BodyModelType]
    values: list[NDArray[np.float64]]

    def __post_init__(self) -> None:
        for value in self.values:
            if value.ndim != 2 or value.shape[1] != 3:
                raise ValueError("Expected shape (n_joints, 3)")

    @property
    def joint_centers(self) -> NDArray[np.float64]:
        return np.mean(self.values, axis=0)

    @override
    @property
    def body_list(self) -> list[NDArray[np.float64]]:
        return self.values
