import os
import json
from datetime import datetime
from pprint import pprint
from tabulate import tabulate
import requests
import pandas as pd
import psutil
from cpuinfo import get_cpu_info
import GPUtil
import logging
from CPU_monitor import IntelPowerGadget, Amd_Power_Log
import csv
from art import *


def get_system_specs():
    # CPU info
    cpu_info = get_cpu_info()
    cpu_codename = cpu_info.get('brand_raw', 'Unknown CPU')

    # RAM info
    ram_info = psutil.virtual_memory()
    ram_size_gb = ram_info.total / (1024 ** 3)  # Convert bytes to GB

    # GPU info
    gpus = GPUtil.getGPUs()
    if gpus:
        gpu_info = gpus[0].name
    else:
        gpu_info = 'No GPU found'

    return {
        'CPU Codename': cpu_info,
        'RAM Size (GB)': round(ram_size_gb, 1),
        'GPU Codename': gpu_info
    }


def is_config_available(config_path):
    """
    Check if the local configuration file is available.

    Parameters:
    config_path (str): The path to the configuration file.

    Returns:
    bool: True if the configuration file exists, False otherwise.
    """
    return os.path.isfile(config_path)


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


def list_projects(config):
    """
    List all projects in the configuration file.

    Parameters:
    config (dict): The configuration data.

    Returns:
    list: The list of project names.
    """
    return list(config.get("Projects", {}).keys())


def select_project(projects):
    """
    Let the user select a project.

    Parameters:
    projects (list): The list of project names.

    Returns:
    str: The selected project name.
    """

    while True:
        try:
            choice = int(input("Enter the number of the project you want to use: "))
            if 1 <= choice <= len(projects):
                return projects[choice - 1]
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")


def get_past_carbon_intensity_electricity_maps(api_token, start, end):
    url = "https://api.electricitymap.org/v3/carbon-intensity/past"
    headers = {
        'auth-token': api_token
    }
    params = {
        'start': start,
        'end': end
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()['data']['carbonIntensity']
    else:
        response.raise_for_status()
    # # Example usage
    # api_token = 'your_api_token_here'
    # zone = 'DE'
    # datetime = '2019-05-21T00:00:00Z'
    #
    # try:
    #     data = get_past_carbon_intensity(api_token, zone, datetime)
    #     print(data)
    # except requests.exceptions.HTTPError as err:
    #     print(f"HTTP error occurred: {err}")
    # except Exception as err:
    #     print(f"An error occurred: {err}")


def get_carbon_intensity_ourworlddata(entity, year, carbon_intensity_df):
    # Filter the DataFrame based on the entity and year
    result = carbon_intensity_df[
        (carbon_intensity_df['Entity'] == entity) & (carbon_intensity_df['Year'] == year)]

    if not result.empty:
        return result['Carbon intensity of electricity - gCO2/kWh'].values[0]
    else:
        return None


def extract_model_from_cpu_string(cpu_string):
    """
    Extracts the model number from the CPU string.

    Args:
        cpu_string (str): The CPU string to extract the model from.

    Returns:
        str: The extracted model number.
    """
    # Split the string by spaces and return the first word that contains a digit
    for part in cpu_string.split():
        if any(char.isdigit() for char in part):
            return part.lower()
    return None


def get_tdp(cpu_string, csv_path):
    """
    Retrieves the TDP value for a given CPU string from a CSV file.

    Args:
        cpu_string (str): The CPU string to search for.
        csv_path (str): The path to the CSV file.

    Returns:
        float: The TDP value of the CPU, or None if not found.
    """
    try:
        # Extract the model number from the CPU string
        model = extract_model_from_cpu_string(cpu_string)
        if not model:
            print(f"No model number found in CPU string: {cpu_string}")
            return None

        # Load the CSV file into a pandas DataFrame
        df = pd.read_csv(csv_path)

        # Print the DataFrame columns for debugging
        print("CSV Columns:", df.columns)

        # Filter the DataFrame to find the row that contains the model number in the 'CPU' column
        matching_row = df[df['Name'].str.contains(model, case=False, na=False)]

        if not matching_row.empty:
            # Extract the TDP value from the matching row
            tdp_value = int(matching_row['Default TDP'].values[0].replace('W', ''))
            return tdp_value
        else:
            print(f"No matching CPU found for model: {model}")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def create_new_project():
    """
    Guide the user through creating a new project.

    Returns:
    dict: The new project data.
    """
    project_name = input("Enter the name of the new project: ")

    print("Choose the monitoring mode:")
    print("1. Bash mode")
    print("2. Direct mode")
    while True:
        try:
            mode_choice = int(input("Enter the number of the monitoring mode: "))
            if mode_choice == 1:
                monitoring_mode = "bash mode"
                break
            elif mode_choice == 2:
                monitoring_mode = "direct mode"
                break
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    # placeholder for the model related settings
    process_based_model_dir = ''
    process_based_model_cmd = ''
    model_start_keystring = ''
    model_end_keystring = ''
    detecting_interval = ''
    process_running_name = ''
    wrapping_mode = ''
    cpu_tdp = ''
    model_name = input("Enter the name of the process-based model: ")
    if mode_choice == 1:
        process_based_model_dir = input("Please input the location (absolute path) to the model: ")
        process_based_model_cmd = input("Please input the exact name (showing in path) of the model: ")
        wrapping_mode = int(input("Which wrapping mode? 1.Key string 2. CLI intel power gadget"))
        if wrapping_mode == 1:
            model_start_keystring = input("Enter the model start key string (from println output): ")
            model_end_keystring = input("Enter the model end key string (from println output): ")
    elif mode_choice == 2:
        detecting_interval = float(input("Please input the desired interval for detecting the status of the model: "
                                         "\n ATTENTION: START the ProcessC program before your Process-based model "
                                         "starts! Also the lower detecting interval may incur more energy usage."))
        process_running_name = input("Please input the name of the model as process.")

    system_spec = get_system_specs()
    cpu_info = system_spec['CPU Codename']['brand_raw']
    ram_info = system_spec['RAM Size (GB)']
    gpu_info = system_spec['GPU Codename']

    if 'amd' in cpu_info.lower():
            # the current user is using AMD cpu so intel power gadget can not be used
            server_or_nonserver = int(input("Is the CPU server or non-server? answer 1:non-server, 2:server"))
            if server_or_nonserver == 1:
                cpu_tdp = get_tdp(cpu_info, './database/AMD_non_server_spec.csv')
                if cpu_tdp is None:
                    cpu_tdp = int(input("Input the default TDP manually here, numbers only."))

            elif server_or_nonserver == 2:
                cpu_tdp = get_tdp(cpu_info, './database/AMD_server_processor_spec.csv')
                if cpu_tdp is None:
                    cpu_tdp = int(input("Input the default TDP manually here, numbers only."))
                ans = int(input('Instance was created using the server CPU from the Cloud Computing provider? 1:Yes, 2:No'))
                if ans == 1:
                    server_usage_ratio = float(input(
                        'please input the ratio of the cores used over the total number of cores'))
                    cpu_tdp = round(server_usage_ratio*cpu_tdp,2)


    region, country = get_location()

    print("Choose the grid carbon intensity data source:")
    print("1. OurWorldData")
    print("2. Electricitymaps")
    print("3. User custom input")
    grid_carbon_intensity = ''
    while True:
        try:
            intensity_choice = int(input("Enter the number of the data source: "))
            if intensity_choice == 1:
                desired_year = int(input("Please inform the desired year"))
                # ourworlddata only has country wide data, not regional
                carbon_intensity_df = pd.read_csv('./database/carbon-intensity-electricity.csv')
                grid_carbon_intensity = get_carbon_intensity_ourworlddata(country, desired_year, carbon_intensity_df)
                break
            elif intensity_choice == 2:
                Electricitymaps_sub = input("Paid subscription available?: yes/no")
                if Electricitymaps_sub == 'yes':
                    token = input("Input your API token for electricity maps.")
                    start = input("Start date for the grid carbon intensity retrival?: ISO format")
                    end = input("end date for the grid carbon intensity retrival?: ISO format")
                    grid_carbon_intensity = get_past_carbon_intensity_electricity_maps(token, start, end)
                break
            elif intensity_choice == 3:
                print("Please input your grid carbon intensity:")
                intensity_choice = float(input("Enter the number of the grid carbon intensity: "))
                grid_carbon_intensity = intensity_choice
                break
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    pue = float(input("What's the PUE value? Default at 1.0"))

    new_project = {
        "name": project_name,
        "monitoring_mode": monitoring_mode,
        "cpu_info": cpu_info,
        "cpu_tdp": cpu_tdp,
        "ram_info": ram_info,
        "gpu_info": gpu_info,
        "region": region,
        "country": country,
        "grid_carbon_intensity": grid_carbon_intensity,
        "PUE": pue,
        'model_name': model_name,
        'model_wrapping_settings': {'process_based_model_dir': process_based_model_dir,
                                    'process_based_model_cmd': process_based_model_cmd,
                                    'bash_mode_wrapping_mode': wrapping_mode,
                                    'model_start_keystring': model_start_keystring,
                                    'model_end_keystring': model_end_keystring,
                                    'detecting_interval': detecting_interval,
                                    'process_running_name': process_running_name}
    }

    return new_project


def check_internet_connection():
    """
    Check if the internet connection is available.

    Returns:
    bool: True if internet is available, False otherwise.
    """
    try:
        requests.get("http://www.google.com", timeout=5)
        return True
    except requests.ConnectionError:
        try:
            requests.get("http://www.baidu.com", timeout=5)
            return True
        except requests.ConnectionError:
            return False


def get_location():
    """
    Get the region and country of the current IP location.

    Returns:
    tuple: (region, country) based on the IP location, or manual input if no internet.
    """
    if check_internet_connection():
        try:
            response = requests.get("http://ip-api.com/json/")
            data = response.json()
            return data.get("regionName", "Unknown"), data.get("country", "Unknown")
        except requests.RequestException:
            print("Could not retrieve location. Please enter manually.")
    else:
        print("No internet connection. Please enter location manually.")

    region = input("Enter your region: ")
    country = input("Enter your country: ")
    return region, country


def is_float(value):
    """Check if the value can be converted to a float."""
    try:
        float(value)
        return True
    except ValueError:
        return False


def parse_gpu_power_csv(file_path='gpu_power_log.csv'):
    """
    Parses the GPU power CSV file and returns the cumulative power.draw in kWh.

    Args:
        file_path (str): The path to the CSV file.

    Returns:
        float: The cumulative power.draw in kWh.
    """
    total_power_draw_watt = 0.0
    count = 0
    start_timestamp = None
    end_timestamp = None

    with open(file_path, mode='r') as file:
        csv_reader = csv.DictReader(file)
        headers = csv_reader.fieldnames

        for row in csv_reader:
            # Strip leading and trailing spaces from the keys and values, handling None values
            row = {key.strip(): value.strip() if value is not None else value for key, value in row.items()}

            # Extract power.draw and timestamp values
            power_draw_str = row.get('power.draw', '').strip()
            timestamp_str = row.get('timestamp', '').strip()

            if is_float(power_draw_str) and timestamp_str:
                power_draw_watt = float(power_draw_str)
                timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S.%f')

                total_power_draw_watt += power_draw_watt
                count += 1

                if start_timestamp is None:
                    start_timestamp = timestamp
                end_timestamp = timestamp

    if count == 0:
        return 0.0  # Return 0 if there are no valid power draw entries

    # Calculate average power draw
    average_power_draw_watt = total_power_draw_watt / count
    # Calculate total duration in hours
    total_duration_hours = (end_timestamp - start_timestamp).total_seconds() / 3600
    # Calculate cumulative energy in kWh
    cumulative_energy_kwh = average_power_draw_watt * total_duration_hours / 1000

    return cumulative_energy_kwh


def save_config(config, config_path):
    """
    Save the updated configuration to the file.

    Parameters:
    config (dict): The updated configuration data.
    config_path (str): The path to the configuration file.
    """
    with open(config_path, 'w') as file:
        json.dump(config, file, indent=4)


def main():
    config_path = 'conf.json'
    print('Welcome to ProcessC, start monitoring your process-based model energy usage and carbon emissions NOW!!!')
    if is_config_available(config_path):
        config = load_config(config_path)
        projects = list_projects(config)
        user_create_new = int(input('Would you like to use existing (1) or create new one (2)? (1/2): '))
        if not projects or user_create_new == 2:
            if not projects:
                print("No projects found in the configuration file.")
            create_project = input("Would you like to create a new project? (yes/no): ").strip().lower()
            if create_project == "yes":
                new_project = create_new_project()
                if "Projects" not in config:
                    config["Projects"] = {}
                config["Projects"][new_project["name"]] = new_project
                save_config(config, config_path)
                print(f"New project '{new_project['name']}' created and saved.")
                return new_project['name'], config["Projects"][new_project["name"]]
            else:
                try:
                    print("No project created. Exiting.")
                except Exception as e:
                    print("No project created. Exiting.")
        else:
            print_existing_projects(config)
            selected_project = select_project(projects)
            print(f"You have selected the project: {selected_project}")

            # Here you can proceed with using the selected project setting
            # For example, you can access its details from the config
            project_settings = config["Projects"][selected_project]
            pprint(f"Settings for {selected_project}: {project_settings}")
            return selected_project, config["Projects"][selected_project]
    else:
        print("Configuration file is not available.")


def start_monitor(desired_project):
    print(f'Now running energy and emission tracking for project {desired_project}')
    config = load_config('conf.json')['Projects']
    setting = config[desired_project]
    logging.basicConfig(level=logging.INFO)
    log_file_path = "intel_power_gadget_log.csv"
    output_dir = "."
    logger = logging.getLogger(__name__)
    if 'amd' in setting['cpu_info'].lower():
        cpu_monitor = Amd_Power_Log(setting['cpu_info'], setting['cpu_TDP'], setting['process_based_model_dir'], setting['process_based_model_cmd'],
                                    setting['monitoring_mode'], setting['process_running_name'], setting['detecting_interval'])
        amd_cpu_usage, duration = cpu_monitor.amd_monitor_usage()
        return amd_cpu_usage, duration
    else:
        if setting['monitoring_mode'] == 'bash mode':
            cmd_to_monitor = 'Python bash_mode.py ' + desired_project
        else:
            cmd_to_monitor = "Python direct_mode.py " + desired_project
        try:
            gadget = IntelPowerGadget(output_dir=output_dir,
                                      log_file_name=log_file_path)

            gadget.start_logging(cmd_to_monitor)
            # time.sleep(2)  # Wait for user input to stop logging
            gadget.stop_logging()
            print(f"Log file created at: {gadget._log_file_path}")
            return None, None
        except Exception as e:
            logger.error(f"Error: {e}")


def calculate_ram_power_usage(ram_gb, duration_sec):
    """
    Calculates the power usage of RAM in kWh given the duration and amount of RAM.

    Args:
        ram_gb (float): The amount of RAM in GB.
        duration_sec (float): The duration in seconds.

    Returns:
        float: The power usage in kWh.
    """
    # Power consumption in watts
    power_consumption_w = (3 * ram_gb) / 8

    # Convert duration from seconds to hours
    duration_hours = duration_sec / 3600

    # Calculate energy consumption in watt-hours
    energy_consumption_wh = power_consumption_w * duration_hours

    # Convert energy consumption to kilowatt-hours
    energy_consumption_kwh = energy_consumption_wh / 1000

    return energy_consumption_kwh


# def res_gen(project_setting_val):
#     # parse the power log
#     cumulative_processor_energy_mwh, total_elapsed_time_sec = parse_intel_power_log()
#     cpu_cumulative_processor_energy_kwh = cumulative_processor_energy_mwh / 1000 if cumulative_processor_energy_mwh else None
#     gpu_kwh = parse_gpu_power_csv()
#     print(f'Elapsed time:{total_elapsed_time_sec} seconds')
#     print(f'CPU energy:{cpu_cumulative_processor_energy_kwh} Kwh')
#     print(f'gpu energy:{gpu_kwh} Kwh')
#     ram_info = psutil.virtual_memory()
#     ram_size_gb = round(ram_info.total / (1024 ** 3), 0)  # Convert bytes to GB
#     ram_power_usage = calculate_ram_power_usage(ram_size_gb, total_elapsed_time_sec)
#     print(f'ram power usage {ram_power_usage} Kwh')
#     total_energy = gpu_kwh + cumulative_processor_energy_mwh + ram_power_usage
#     print(f'Total energy usage for running the model is {total_energy} Kwh')
#     total_emission = project_setting_val['grid_carbon_intensity'] * total_energy
#     grid_carbon_intensity = project_setting_val['grid_carbon_intensity']
#     print(f'Total carbon emission for running the model is {total_emission} g/CO2 Eq\n '
#           f'under grid carbon intensity of {grid_carbon_intensity}')

def res_gen(project_setting_val, project_name_val, cpu_usage, total_elapsed_time_sec):
    # Parse the power log
    if cpu_usage is None:
        cumulative_processor_energy_kwh, total_elapsed_time_sec = parse_intel_power_log()
    else:
        cumulative_processor_energy_kwh = cpu_usage
        total_elapsed_time_sec = total_elapsed_time_sec

    # parse the power usage from the graphic card log
    gpu_kwh = parse_gpu_power_csv()

    # RAM info and power usage
    ram_info = psutil.virtual_memory()
    ram_size_gb = round(ram_info.total / (1024 ** 3), 0)  # Convert bytes to GB
    ram_power_usage = calculate_ram_power_usage(ram_size_gb, total_elapsed_time_sec)

    # Total energy and emission
    total_energy = gpu_kwh + cumulative_processor_energy_kwh + ram_power_usage
    grid_carbon_intensity = project_setting_val['grid_carbon_intensity']
    total_emission = grid_carbon_intensity * total_energy

    # Prepare data for the table
    table_data = [
        ["Project_name", project_name_val],
        ["Elapsed Time (seconds)", total_elapsed_time_sec],
        ["CPU Energy (kWh)", cumulative_processor_energy_kwh],
        ["GPU Energy (kWh)", gpu_kwh],
        ["RAM Power Usage (kWh)", ram_power_usage],
        ["Total Energy Usage (kWh)", total_energy],
        ["Grid Carbon Intensity (g/CO2 Eq)", grid_carbon_intensity],
        ["Total Carbon Emission (g/CO2 Eq)", total_emission]
    ]

    # Print the table
    print(tabulate(table_data, headers=["Metric", "Value"], tablefmt="grid"))

    # output to local csv
    df = pd.DataFrame(table_data, columns=["Metric", "Value"])

    # Save the DataFrame to a CSV file
    df.to_csv('./monitoring_output/' + project_name_val + '.csv', index=False)


def parse_intel_power_log(file_path='intel_power_gadget_log.csv'):
    """
    Parses the Intel Power Gadget log CSV file and returns the final Cumulative Processor Energy_0 (kWh) and Total Elapsed Time (sec).

    Args:
        file_path (str): The path to the CSV file.

    Returns:
        tuple: A tuple containing the final Cumulative Processor Energy_0 (kWh) and Total Elapsed Time (sec).
    """
    cumulative_processor_energy_mwh = 0.0
    total_elapsed_time_sec = 0.0

    with open(file_path, mode='r') as file:
        for line in file:
            line = line.strip()
            # print(f"Processing line: {line}")  # Print each line for debugging\
            if 'Total Elapsed Time (sec)' in line:
                try:
                    total_elapsed_time_sec = float(line.split('=')[-1].strip())
                except ValueError as e:
                    print(f"Error parsing Total Elapsed Time (sec): {e}")

            if 'Cumulative Processor Energy_0 (mWh)' in line:
                try:
                    cumulative_processor_energy_mwh = float(line.split('=')[-1].strip())
                except ValueError as e:
                    print(f"Error parsing Cumulative Processor Energy_0 (mWh): {e}")

    # Convert cumulative processor energy from mWh to kWh
    cumulative_processor_energy_kwh = cumulative_processor_energy_mwh / 1_000_000

    return cumulative_processor_energy_kwh, total_elapsed_time_sec


def print_existing_projects(projects):
    """
    Prints existing projects in the format {1: 'test3.....'}

    Args:
        projects (dict): A dictionary containing project information.
    """
    project_list = list(projects['Projects'].keys())
    formatted_projects = {i + 1: project for i, project in enumerate(project_list)}

    for key, value in formatted_projects.items():
        print(f"{key}: '{value}'")


def print_welcome():
    tprint('ProcessC beta 1.0 @McGill')


if __name__ == "__main__":
    print_welcome()
    project_name, project_setting = main()
    ans = int(input('Continue the monitoring process with the selected project (1) or terminate ProcessC (2)?'))
    if ans == 1:
        cpu_usage, duration = start_monitor(project_name)
        res_gen(project_setting, project_name, cpu_usage, duration)
    else:
        print('ProcessC terminated')

