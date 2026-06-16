import logging
import os

from habmoti import InterfaceCli


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(filename)s - %(levelname)s - %(message)s")
    logging.info("Starting the analyzer...")
    logging.warning("Starting the analyzer...")

    config_filepath = os.environ.get("HABMOTI_CONFIG_FILE")
    InterfaceCli().exec_from_config(config_filepath) if config_filepath else InterfaceCli().exec()


if __name__ == "__main__":
    main()
