import gpustat
import time
import threading
import logging
import datetime
import csv

logger = logging.getLogger(__name__)


class NvidiaPowerMonitor:
    def __init__(self, log_file="gpu_power_log.csv"):
        self.log_file = log_file
        self.monitor_thread = None
        self._stop_event = threading.Event()
        self.measurements = []

    def _monitor_power(self, interval):
        """
        Monitors GPU power usage and logs it at specified intervals.
        """
        with open(self.log_file, 'w', newline='') as csvfile:
            fieldnames = ['timestamp', 'gpu', 'power.draw', 'power.limit']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            while not self._stop_event.is_set():
                stats = gpustat.new_query()
                for gpu in stats.gpus:
                    measurement = {
                        'timestamp': datetime.datetime.now(),
                        'gpu': gpu.index,
                        'power.draw': gpu.power_draw,
                        # 'power.limit': gpu.enforced_power_limit
                    }
                    writer.writerow(measurement)
                    self.measurements.append(measurement)
                    logger.info(f"Logged power usage for GPU {gpu.index}: {measurement}")
                time.sleep(interval)

    def start_monitoring(self, interval=1):
        """
        Starts the GPU power monitoring in a separate thread.
        """
        self._stop_event.clear()
        self.monitor_thread = threading.Thread(target=self._monitor_power, args=(interval,))
        self.monitor_thread.start()
        logger.info(f"Started GPU power monitoring, logging to {self.log_file}")

    def stop_monitoring(self):
        """
        Stops the GPU power monitoring process.
        """
        self._stop_event.set()
        if self.monitor_thread is not None:
            self.monitor_thread.join()
        logger.info("Stopped GPU power monitoring")

    def get_measurements(self):
        """
        Returns the recorded measurements.
        """
        return self.measurements


# Example usage
def main():
    logging.basicConfig(level=logging.INFO)
    log_file_path = "gpu_power_log.csv"

    try:
        monitor = NvidiaPowerMonitor(log_file=log_file_path)
        monitor.start_monitoring(interval=1)
        print("GPU power monitoring started. Press Enter to stop monitoring...")
        time.sleep(1)

        monitor.stop_monitoring()
        # measurements = monitor.get_measurements()
        print(f"Log file created at: {log_file_path}")

    except Exception as e:
        logger.error(f"Error: {e}")


if __name__ == "__main__":
    main()
