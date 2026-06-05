import logging
from pathlib import Path
import queue
import time
import threading

from .data.frame_data import FrameData
from .analyses.analyzer import Analyzer, EmptyAnalyzer
from .kinematics.body_kinematics_device import BodyKinematicsDevice
from .viewers.viewer import Viewer

_logger = logging.getLogger(__name__)


class Habmoti:
    def __init__(
        self,
        body_kinematics_device: BodyKinematicsDevice,
        analyzer: Analyzer | None = None,
        viewer: Viewer | None = None,
        save_path: Path | None = None,
    ):
        self._body_kinematics_device = body_kinematics_device
        self._analyzer = analyzer if analyzer is not None else EmptyAnalyzer()
        self._viewer = viewer
        self._save_path = save_path

        self._to_analyse_queue = queue.Queue()
        self._to_save_queue = None
        if self._has_writer:
            self._to_save_queue = queue.Queue()
        self._to_view_queue = queue.Queue()

        self._stop_event = threading.Event()
        self._capture_is_over_event = threading.Event()
        self._analysis_loop_is_over_event = threading.Event()

    def start(self) -> None:
        """
        Start the pipeline threads.
        """

        self._stop_event.clear()
        self._capture_is_over_event.clear()
        self._analysis_loop_is_over_event.clear()

        self.threads = [
            threading.Thread(target=self._capture_loop, daemon=False),
            threading.Thread(target=self._analysis_loop, daemon=False),
        ]
        if self._has_viewer:
            self.threads.append(threading.Thread(target=self._view_loop, daemon=False))
        if self._has_writer:
            self.threads.append(threading.Thread(target=self._writer_loop, daemon=False))

        for t in self.threads:
            t.start()

    def stop(self):
        """
        Stop the pipeline threads.
        """
        self._stop_event.set()

        for t in self.threads:
            t.join()

    def _capture_loop(self) -> None:
        """
        Capture loop: continuously capture data from the device and put it in the queue.
        """
        try:
            self._body_kinematics_device.start()

            while not self._stop_event.is_set():
                try:
                    frame_data = FrameData(
                        timestamp=int(time.time() * 1000),
                        body_kinematics=self._body_kinematics_device.get_current_body_kinematics(),
                    )
                    self._to_analyse_queue.put(frame_data)
                    if self._has_viewer:
                        self._to_view_queue.put(frame_data)

                except Exception as e:
                    _logger.error("Capture error:", exc_info=e)

            self._body_kinematics_device.stop()

        finally:
            self._capture_is_over_event.set()

    def _analysis_loop(self) -> None:
        """
        Analysis loop: continuously get frames from the queue and analyze them.
        When the capture is over, the loop continues until the queue is empty then stops.
        """
        try:
            while not self._capture_is_over_event.is_set() or not self._to_analyse_queue.empty():
                try:
                    frame: FrameData = self._to_analyse_queue.get(timeout=0.5)
                    self._analyzer.perform(frame)
                    if self._has_writer:
                        self._to_save_queue.put(frame)
                except queue.Empty:
                    continue
        finally:
            self._analysis_loop_is_over_event.set()

    @property
    def _has_viewer(self) -> bool:
        return self._viewer is not None

    def _view_loop(self) -> None:
        """
        View loop: continuously get frames from the queue and display them.
        When the capture is over, the loop continues until the queue is empty then stops.
        """
        while not self._capture_is_over_event.is_set() or not self._to_view_queue.empty():
            try:
                frame: FrameData = self._to_view_queue.get(timeout=0.5)
                if self._viewer is not None:
                    self._viewer.display(frame)
            except queue.Empty:
                continue

    @property
    def _has_writer(self) -> bool:
        return self._save_path is not None

    def _writer_loop(self) -> None:
        """
        Write frames to disk.
        """

        self._save_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._save_path, "w") as f:
            while not self._analysis_loop_is_over_event.is_set() or not self._to_save_queue.empty():
                try:
                    # Append the frame data to the file
                    frame: FrameData = self._to_save_queue.get(timeout=0.5)
                    f.write(str(frame.serialize().values()) + "\n")

                except queue.Empty:
                    continue
