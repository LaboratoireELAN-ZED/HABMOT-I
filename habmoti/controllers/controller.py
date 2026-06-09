from abc import ABC, abstractmethod
from typing import override, TYPE_CHECKING

if TYPE_CHECKING:
    from ..data.frame_data import FrameData
    from ..habmoti import Habmoti


class Controller(ABC):
    @abstractmethod
    def start(self, habmoti: Habmoti) -> None:
        """
        Start the controller. This is called before the first frame is received.
        """
        pass

    @abstractmethod
    def perform(self, frame_data: FrameData | None) -> None:
        """
        Perform a control action based on a frame of data.
        """

    @abstractmethod
    def stop(self) -> None:
        """
        Stop the controller. This is called when the controller is no longer needed.
        """
        pass


class ControllerList(Controller):
    def __init__(self, controllers: list[Controller] = None):
        self._controllers = controllers if controllers is not None else []
        self._is_locked = False

    def append(self, controller: Controller) -> None:
        if self._is_locked:
            raise RuntimeError("Cannot append a controller to a locked ControllerList")
        self._controllers.append(controller)

    @override
    def start(self, habmoti: Habmoti) -> None:
        self._is_locked = True
        for controller in self._controllers:
            controller.start(habmoti=habmoti)

    @override
    def perform(self, frame_data: FrameData | None) -> None:
        for controller in self._controllers:
            controller.perform(frame_data)

    @override
    def stop(self) -> None:
        for controller in self._controllers:
            controller.stop()
        self._is_locked = False
