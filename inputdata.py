from ship import Ship
from ops import OPS
import datetime
import os
import json
import pandas as pd
import random
import datetime
from reefer import Reefer
from chargers import Charger
from vehicles import Vehicle
from vehicles import VehicleJob
from yardcrane import YardCrane
from yardcrane import YCJob
import math


class InputData:
    def __init__(self):
        self.case_name = str()
        self.berths = list()
        self.berth_plan = list()
        self.OPSs = list()
        self.nodes = list()
        self.reefers = list()
        self.ambient_temperature = dict()
        self.vehicles = list()
        self.chargers = list()
        self.cranes = list()
        self.timestep = datetime.timedelta()
        self.date_time = list()
        self.raw_data = dict()

    def read_input_data(self, case_name):
        self.case_name = case_name
        case_dir = os.path.join('data', self.case_name)

        # Read json files
        files = os.listdir(case_dir)
        files = [f for f in files if os.path.isfile(os.path.join(case_dir, f))]
        _read_json_files(self.raw_data, files, case_dir)

        # Read berth allocation input (includes information about OPS systems and ships
        position_filename = os.path.join(case_dir, f'position.csv')
        demand_filename = os.path.join(case_dir, f'demand.csv')
        berth_allocation_input = pd.read_csv(position_filename)
        demand_input = pd.read_csv(demand_filename)
        _read_berth_allocation_input(self.raw_data, berth_allocation_input, demand_input)

        # Read YCs input
        cranes_activities_filename = os.path.join(case_dir, f'cranes_activity.csv')
        cranes_activities_input = pd.read_csv(cranes_activities_filename)
        _read_cranes_activities_input(self.raw_data, cranes_activities_input, demand_input)

    def preprocessing_input_data(self):
        self.berths = self.raw_data['Berths']
        _preprocess_general_data(self, self.raw_data['general_data'])
        _preprocess_reefers_data(self, self.raw_data['reefers_data'])
        _preprocess_vehicles_data(self, self.raw_data['vehicles_data'])
        _preprocessing_berth_allocation(self, self.raw_data['OPS'], self.raw_data['Berth plan'])
        _preprocess_yc_data(self, self.raw_data['YC'], self.date_time)

    def __getitem__(self, item):
        if "OPS" in item:
            for ops in self.OPSs:
                if ops.name == item:
                    return ops
            return print(f"OPS f{item} does not exist")
        elif "Ship" in item:
            for ship in self.berth_plan:
                if ship.name == item:
                    return ship
            return print(f"Ship f{item} does not exist")
        elif "Reefer" in item:
            for reefer in self.reefers:
                if reefer.name == item:
                    return reefer
            return print(f"Reefer f{item} does not exist")
        elif "Charger" in item:
            for charger in self.chargers:
                if charger.name == item:
                    return charger
            return print(f"Charger f{item} does not exist")
        elif "Vehicle" in item:
            for vehicle in self.vehicles:
                if vehicle.name == item:
                    return vehicle
            return print(f"Vehicle f{item} does not exist")
        elif "YC" in item:
            for crane in self.cranes:
                if crane.name == item:
                    return crane
            return print(f"Crane f{item} does not exist")


# ======================================================================================================================
#   Read input data
# ======================================================================================================================
def _read_json_files(raw_data, files, directory):
    for filename in files:
        if os.path.splitext(os.path.basename(filename))[1] == ".json":
            with open(os.path.join(directory, filename), 'r') as json_file:
                raw_data[os.path.splitext(os.path.basename(filename))[0]] = json.load(json_file)


def _read_berth_allocation_input(raw_data, berth_allocation, demand):
    berth_allocation = berth_allocation[(berth_allocation['type'] == "Navire") &
                                        (berth_allocation['noeud'] != "V")]
    berth_allocation = berth_allocation[['ref', 'noeud']]

    # Extracting data about berths
    berths_list = list(berth_allocation['noeud'].drop_duplicates())
    raw_data['Berths'] = berths_list

    # Extracting OPS input data
    # - Assume that each berth has an OPS system with the name containing berth name
    # - Maximum OPS power is extracted from "demand.csv"
    # - Bus index in electrical network is assumed to be 1, as the real data is currently absent
    OPSs = []
    for ops in berths_list:
        ops_params = {"Name": f"OPS {ops}",
                      "Maximum power": demand[f"{ops}_Capacity"][0],
                      "Berth": f"Berth {ops}",
                      "Bus index in electrical network": 1}
        OPSs.append(ops_params)
    raw_data['OPS'] = OPSs

    # Extracting berth plan
    ships_list = list(berth_allocation['ref'].drop_duplicates())
    ships = []
    for ship in ships_list:
        allocated_berth = berth_allocation[berth_allocation['ref'] == ship]["noeud"].values[0]
        allocated_berth = f"Berth {allocated_berth}"
        # Arrival time is when the demand of the ship first appears (non-zero) in the column corresponding to the ship demand
        arrival = demand[demand[ship] != 0]["Unnamed: 0"].values[0]
        arrival = datetime.datetime.strptime(arrival[:-9], '%Y-%m-%d %H:%M')
        # Berth time is the total number of non-zero element in the column corresponding to the ship demand
        berth_time = demand[demand[ship] != 0].shape[0]
        berth_time = datetime.timedelta(hours=berth_time)
        # Minimum OPS power from OPS is assumed to be 60% of the total ship's consumption
        min_ops_power = demand[demand[ship] != 0][ship].sum() * 0.6
        consumption = list(demand[demand[ship] != 0][ship])
        ship_params = {'Name': f"Ship {ship}",
                       'Allocated berth': allocated_berth,
                       'Arrival time': arrival,
                       'Berth time': berth_time,
                       'Minimum OPS energy': min_ops_power,  # kWh
                       'Power consumption': consumption,  # kW
                       }
        ships.append(ship_params)
    raw_data['Berth plan'] = ships


def _read_cranes_activities_input(raw_data, cranes_activities, demand):
    cranes_list = cranes_activities['Crane'].drop_duplicates()
    cranes = []
    for crane in cranes_list:
        # Bus index and maximum power are assumed
        bus_indx = 2
        max_power = 7000
        job_list = cranes_activities[cranes_activities['Crane'] == crane]
        job_plan = []
        for job_indx in job_list.index:
            # Type of the job is random because there is no data
            job_type = random.choices(['Loading', 'Unloading', 'Rearrangement'],
                                      weights=(25, 25, 50), k=1)[0]
            start = job_list['Start'][job_indx]
            start = datetime.datetime.strptime(start[:19], '%Y-%m-%d %H:%M:%S')
            end = job_list['End'][job_indx]
            end = datetime.datetime.strptime(end[:19], '%Y-%m-%d %H:%M:%S')
            energy = max(demand[crane])
            job_plan_params = {'Type of action': job_type,
                               'Energy': energy,
                               'Start': start,
                               'End': end
                               }
            job_plan.append(job_plan_params)
        crane_params = {'Name': f"YC {crane}",
                        'Bus index in electrical network': bus_indx,
                        'Maximum power': max_power,
                        'Job plan': job_plan,
                        }
        cranes.append(crane_params)
    raw_data['YC'] = cranes


# ======================================================================================================================
#   Preprocess input data
# ======================================================================================================================
def _preprocess_general_data(input_data, raw_general_data):
    # Nodes
    input_data.nodes = raw_general_data['nodes']

    # Timestep
    hours = raw_general_data['timestep']['hours']
    minutes = raw_general_data['timestep']['minutes']
    seconds = raw_general_data['timestep']['seconds']
    input_data.timestep = datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds)

    # Time intervals
    for time in raw_general_data['time_intervals']:
        input_data.date_time.append(datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S'))

    # Ambient temperature
    for time in raw_general_data['time_intervals']:
        time_datetime = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
        temperature = raw_general_data['ambient_temperature'][time]
        input_data.ambient_temperature[time_datetime] = temperature


def _preprocess_reefers_data(input_data, raw_reefers_data):
    for reefer_group in raw_reefers_data:
        reefer = Reefer()
        reefer.extract_data_from_dict(reefer_group)
        reefer.compute_baseload_and_internal_temperature(input_data.ambient_temperature, input_data.timestep)
        input_data.reefers.append(reefer)


def _preprocess_vehicles_data(input_data, raw_vehicles_data):
    for charger_input in raw_vehicles_data['Chargers']:
        charger = Charger()
        charger.extract_data_from_dict(charger_input)
        input_data.chargers.append(charger)

    for vehicle_input in raw_vehicles_data['Vehicles']:
        vehicle = Vehicle()
        vehicle.extract_data_from_dict(vehicle_input)
        for job_input in vehicle_input['Job plan']:
            job = VehicleJob()
            job.extract_data_from_dict(job_input)
            job.compute_baseload_and_SOC_profiles(vehicle, input_data.chargers)
            vehicle.job_plan.append(job)
        vehicle.extract_SOC_profile_from_jobs()
        input_data.vehicles.append(vehicle)

    for charger in input_data.chargers:
        baseload_profile = dict()
        for vehicle in input_data.vehicles:
            for job in vehicle.job_plan:
                if (job.type == 'Charging') and (job.location == charger.name):
                    baseload_profile.update(job.baseload)
        charger.baseload = baseload_profile


def _preprocessing_berth_allocation(input_data, raw_ops_data, raw_berth_plan):
    for ship_at_berth in raw_berth_plan:
        ship = Ship()
        ship.extract_data_from_dict(ship_at_berth)
        ship.compute_ship_baseload_profile()
        input_data.berth_plan.append(ship)

    for ops_input in raw_ops_data:
        ops = OPS()
        ops.extract_data_from_dict(ops_input)
        ops.compute_ops_baseload_profile(input_data.berth_plan)
        input_data.OPSs.append(ops)


def _preprocess_yc_data(input_data, raw_yc_data, time_intervals):
    for crane_input in raw_yc_data:
        crane = YardCrane()
        crane.extract_data_from_dict(crane_input)
        for job_input in crane_input['Job plan']:
            job = YCJob()
            job.extract_data_from_dict(job_input)
            crane.job_plan.append(job)
        crane.compute_yc_baseload_profile(time_intervals)
        input_data.cranes.append(crane)
