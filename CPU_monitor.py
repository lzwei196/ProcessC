import os
import sys
import shutil
import subprocess
import logging
import time

import psutil

from gpu_monitor import NvidiaPowerMonitor

shortcut_path = 'C:\\Users\\lzwei\\OneDrive\\Desktop\\IntelPowerGadget.exe-autolog.lnk'
logger = logging.getLogger(__name__)


class IntelPowerGadget:
    _osx_exec = "PowerLog"
    _osx_exec_backup = "/Applications/Intel Power Gadget/PowerLog"
    _windows_exec = "PowerLog3.0.exe"
    _windows_exec_backup = "C:\\Program Files\\Intel\\Power Gadget 3.6\\PowerLog3.0.exe"

    def __init__(
            self,
            output_dir: str = ".",
            resolution: int = 100,
            log_file_name: str = "intel_power_gadget_log.csv",
    ):
        self._log_file_path = os.path.join(output_dir, log_file_name)
        self._system = sys.platform.lower()
        self._resolution = resolution
        self._setup_cli()
        self.process = None

    def _setup_cli(self):
        """
        Setup CLI command to run Intel Power Gadget
        """
        if self._system.startswith("win"):
            if shutil.which(self._windows_exec):
                self._cli = shutil.which(self._windows_exec)  # Windows exec is a relative path
            elif os.path.exists(self._windows_exec_backup):
                self._cli = self._windows_exec_backup
            else:
                raise FileNotFoundError(
                    f"Intel Power Gadget executable not found on {self._system}"
                )
        elif self._system.startswith("darwin"):
            if shutil.which(self._osx_exec):
                self._cli = self._osx_exec
            elif os.path.exists(self._osx_exec_backup):
                self._cli = self._osx_exec_backup
            else:
                raise FileNotFoundError(
                    f"Intel Power Gadget executable not found on {self._system}"
                )
        else:
            raise SystemError("Platform not supported by Intel Power Gadget")

    def _log_values(self, cmd):
        """
         Logs output from Intel Power Gadget command line to a file
         """
        logger.info(f"Executing command: {cmd}")

        if self._system.startswith("win"):
            self.process = subprocess.Popen(
                [
                    self._cli,
                    "-resolution",
                    str(self._resolution),
                    "-file",
                    self._log_file_path,
                    "-cmd",
                    f"cmd /c {cmd}"
                ],
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        elif self._system.startswith("darwin"):
            command = f"'{self._cli}'  -resolution {self._resolution} -file {self._log_file_path}  -cmd {cmd}> /dev/null"
            # command = f"'{self._cli}' -resolution {self._resolution} -file {self._log_file_path} > /dev/null"
            self.process = subprocess.Popen(command, shell=True)

        # Capture the output of the process
        stdout, stderr = self.process.communicate()
        self.script_output = stdout.decode().strip() if stdout else stderr.decode().strip()

        # print(self.script_output)
        # Wait for the process to finish
        self.process.wait()
        return self.script_output

    def start_logging(self, cmd):
        """
        Starts the logging process
        """
        self._log_values(cmd)
        logger.info(f"Started logging to {self._log_file_path}")

    def stop_logging(self):
        """
        Stops the logging process
        """
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
                logger.info("Successfully terminated the logging process.")
            except subprocess.TimeoutExpired:
                logger.warning("Process did not terminate in time, killing it.")
                self.process.kill()


class Amd_Power_Log:
    def __init__(
            self,
            cpu_model,
            cpu_tdp,
            program_path,
            program_name,
            monitoring_mode,
            program_running_name,
            detecting_interval
    ):
        self.cpu = cpu_model
        self.cpu_tdp = cpu_tdp
        self.program_path = program_path
        self.program_name = program_name
        self.monitoring_mode = monitoring_mode
        self.program_running_name = program_running_name
        self.detecting_interval = detecting_interval
    # For AMD cpus on Windows, the power log could not be used, so the defaultTDP was used to estimate the CPU usage

    def amd_monitor_usage(self):
        rz_path = os.path.join(self.program_path, self.program_name)
        cmd_path = self.program_path
        try:
            # use keyword or use the cmd command directly for running the powerlog from power gadget
            # current setting the bash mode includes the initiation of the GPU logging module
            start_time = time.time()
            gpu_monitor = NvidiaPowerMonitor()
            if self.monitoring_mode.lower() == 'bash mode':
                gpu_monitor.start_monitoring()
                subprocess.run(rz_path, cwd=r'{}'.format(cmd_path))
                gpu_monitor.stop_monitoring()
                end_time = time.time()
                duration = round(end_time - start_time, 2)
                print(f"Simulation completed in {duration} seconds.")
                cpu_energy_usage = self.cpu_tdp*duration/(3600*1000)
                return cpu_energy_usage, duration
            elif self.monitoring_mode.lower() == 'direct mode':
                    start_time = time.time()
                    process_name = self.program_running_name
                    interval = self.detecting_interval
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
                                end_time = time.time()
                                duration = round(end_time - start_time, 2)
                                print(f"Simulation completed in {duration} seconds.")
                                cpu_energy_usage = self.cpu_tdp * duration / (3600 * 1000)
                                return cpu_energy_usage, duration
                        time.sleep(interval)

        except Exception as e:
            print(e)


if __name__ == "__main__":
    # example usage
    # make sure the intel power gadget is installed, check the version number
    logging.basicConfig(level=logging.INFO)
    log_file_path = "intel_power_gadget_log.csv"
    output_dir = "."
    cmd_to_monitor = "Python bash_mode.py test7"
    try:
        gadget = IntelPowerGadget(output_dir=output_dir,
                                  log_file_name=log_file_path)
        gadget.start_logging(cmd_to_monitor)
        # time.sleep(2)  # Wait for user input to stop logging
        gadget.stop_logging()
        print(f"Log file created at: {gadget._log_file_path}")
    except Exception as e:
        logger.error(f"Error: {e}")
