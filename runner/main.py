import os
from pathlib import Path
from time import sleep

from habmoti import Habmoti, MockedZedDevice, ToConsoleAnalyzer


def main():
    device = MockedZedDevice(
        configuration_filepath=Path(os.getenv("HABMOTI_CONFIG_PATH")), target_fps=10, max_fps_lag_ms=0
    )
    analyzer = ToConsoleAnalyzer()
    save_path = Path(os.getenv("HABMOTI_SAVE_PATH"))

    habmoti = Habmoti(body_kinematics_device=device, analyzer=analyzer)  # , save_path=save_path)

    habmoti.start()
    sleep(10)
    habmoti.stop()


if __name__ == "__main__":
    main()
