import json
import sys

import psutil
import time
import logging
from gpu_monitor import NvidiaPowerMonitor

logger = logging.getLogger(__name__)


# detecting interval defaulted at 0.1 second
def wait_for_process(process_name, interval=0.1):
    gpu_monitor = NvidiaPowerMonitor()
    """
    Waits for a process to start and then terminate.

    Args:
        process_name (str): The name of the process to monitor.
        interval (int): The interval (in seconds) at which to check for the process.
    """
    process_started = False

    while True:
        # Check if the process is running
        for process in psutil.process_iter(['name']):
            try:
                if process.info['name'] == process_name:
                    if not process_started:
                        logger.info(f"Process {process_name} has started.")
                        process_started = True
                        gpu_monitor.start_monitoring()
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        else:
            if process_started:
                logger.info(f"Process {process_name} has terminated.")
                gpu_monitor.stop_monitoring()
                return
        time.sleep(interval)


def load_config(config_path):
    """
    Load the configuration file.

    Parameters:
    config_path (str): The path to the configuration file.

    Returns:
    dict: The configuration data.
    """
    with open(config_path, 'r') as file:
        config = json.load(file)
    return config


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # have the main function pass which project to use
    arg1 = sys.argv[1]
    setting = load_config('conf.json')['Projects'][arg1]
    process_name = setting['model_wrapping_settings']['process_running_name']
    detect_interval = setting['model_wrapping_settings']['detecting_interval']
    wait_for_process(process_name, )
    print(f"Process {process_name} has started and terminated.")
