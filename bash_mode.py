import json
import sys
import time
import subprocess
from CPU_monitor import IntelPowerGadget
from gpu_monitor import NvidiaPowerMonitor
import threading
import os


def start_simulation_and_monitor(rz_dir, gpu_monitor, wrapping_mode,
                                 starting_line, ending_line, model_name):
    rz_path = os.path.join(rz_dir, model_name)
    cmd_path = rz_dir
    try:
        # use keyword or use the cmd command directly for running the powerlog from power gadget
        # current setting the bash mode includes the initiation of the GPU logging module
        start_time = time.time()
        if wrapping_mode == 2:
            gpu_monitor.start_monitoring()
            subprocess.run(rz_path, cwd=r'{}'.format(cmd_path))
            gpu_monitor.stop_monitoring()
            end_time = time.time()
            duration = round(end_time - start_time, 2)
            print(f"Simulation completed in {duration} seconds.")

        elif wrapping_mode == 1:
            cpu_monitor = IntelPowerGadget()

            process = subprocess.Popen(rz_path, cwd=r'{}'.format(cmd_path), stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE, text=True)

            def process_output(stream, func_map):
                for line in iter(stream.readline, ''):
                    print(line, end='')  # Print the line for real-time feedback
                    for key, func_list in func_map.items():
                        if key in line:
                            for func in func_list:
                                func()

            # Mapping strings to the respective methods without calling them immediately
            func_map = {
                # " ====>  INITIAL VALUES READ IN": [cpu_monitor.start_logging, gpu_monitor.start_monitoring],
                # "NORMAL TERMINATION": [cpu_monitor.stop_logging, gpu_monitor.stop_monitoring]
                starting_line: [cpu_monitor.start_logging, gpu_monitor.start_monitoring],
                ending_line: [cpu_monitor.stop_logging, gpu_monitor.stop_monitoring]
            }

            stdout_thread = threading.Thread(target=process_output, args=(process.stdout, func_map))
            stderr_thread = threading.Thread(target=process_output,
                                             args=(process.stderr, {}))  # Handle stderr similarly if needed

            stdout_thread.start()
            stderr_thread.start()

            stdout_thread.join()
            stderr_thread.join()

            process.wait()

            end_time = time.time()
            duration = round(end_time - start_time, 2)
            print(f"Simulation completed in {duration} seconds.")

    except Exception as e:
        print(e)
        duration = None
    return duration


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


if __name__ == "__main__":
    # cpu_monitor = IntelPowerGadget()
    # have the main function pass which project to use
    arg1 = sys.argv[1]
    # arg1 = 'test7'
    print(arg1)
    setting = load_config('conf.json')['Projects']
    setting = setting[arg1]
    gpu_monitor = NvidiaPowerMonitor()
    # rz_dir = 'C:\\RZWQM2\\alfred\\alfred'
    setting = setting['model_wrapping_settings']
    model_dir = setting['process_based_model_dir']
    cmd = setting['process_based_model_cmd']
    starting_key_string = setting['model_start_keystring']
    ending_key_string = setting['model_end_keystring']
    wrapping_mode = setting['bash_mode_wrapping_mode']
    model_execute_name = setting['process_based_model_cmd']
    start_simulation_and_monitor(model_dir, gpu_monitor, wrapping_mode, starting_key_string, ending_key_string,
                                 model_execute_name)
