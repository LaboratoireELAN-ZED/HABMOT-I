from time import time
from typing import override, TYPE_CHECKING

from .controller import Controller

if TYPE_CHECKING:
    from .controller import Habmoti, FrameData


class StopDataCollectionController(Controller):
    def __init__(self, max_runtime: float = None, stop_if_data_runs_out: bool = True):
        super().__init__()
        self._habmoti: Habmoti | None = None
        self._is_stopped = True

        self._max_runtime = max_runtime
        self._stop_if_data_runs_out = stop_if_data_runs_out
        self._start_time = None

    @override
    def start(self, habmoti: Habmoti) -> None:
        """
        Start the analyzer. This is called before the first frame is analyzed.
        """
        self._habmoti = habmoti
        self._is_stopped = False
        self._start_time = time()

    @override
    def perform(self, frame_data: FrameData | None) -> None:
        """
        Analyze a frame of data.

        Args:
            frame_data: The data to analyze. The analysis is stored in the frame_data itself
        """
        if not self._is_stopped:
            stopped_collecting = self._stop_if_data_runs_out and frame_data is None
            has_timed_out = self._max_runtime is not None and (time() - self._start_time) > self._max_runtime
            if stopped_collecting or has_timed_out:
                self._habmoti.stop()
                self._is_stopped = True

    @override
    def stop(self) -> None:
        """
        Stop the analyzer. This is called when the analyzer is no longer needed.
        """
        self._habmoti = None
        self._is_stopped = True
