import pandas as pd
import random
import json


# *************************************************************
# This part of the code creates several JSON files with the dummy data to provide input for the load flexibility tool
# due to the lack of the real data.
# *************************************************************

# To define a calculation period, the first 24 time steps were extracted from one of the input data files (
# particularly, from demand.csv) Assumed that the timestep is equal to 1 hour. Otherwise, it should be calculated
# within this function, or manually provided in general_data['timestep'] below
def define_calculation_period():
    demand_input = pd.read_csv("data/testcase/demand.csv")
    time_intervals = [t[:-6] for t in demand_input['Unnamed: 0'][:24]]
    return time_intervals


# ======================================================================================================================
#   General data
# ======================================================================================================================
# Create dictionary of the prospect JSON file
general_data = dict()
general_data['nodes'] = [1, 2, 3, 4]
general_data['time_intervals'] = define_calculation_period()
general_data['timestep'] = {'hours': 1,
                            'minutes': 0,
                            'seconds': 0}
general_data['ambient_temperature'] = {timestep: random.randint(10, 15) for timestep in general_data['time_intervals']}
filename = "data/testcase/general_data.json"
with open(filename, 'w') as json_file:
    json.dump(general_data, json_file, indent=4)

# ======================================================================================================================
#   Reefers data
# ======================================================================================================================

# surface = (2.89 * 2.44 + 12.19 * 2.89 + 12.19 * 2.44) * 2
reefers_data = [{'Group': 'Reefer group 1',
                 'Number of containers': 100,
                 'Mass of reefer content': 20000,  # kg per one container (avg)
                 'Heat capacity': 1760,  # J/(kg*Celsius)
                 'Surface area': 74.97,  # m^2
                 'Heat transition coefficient': 0.5,  # W/m^2Celsius
                 'Initial temperature': 5,  # degree Celsius
                 'Upper bound': 5,  # degree Celsius
                 'Lower bound': 2,  # degree Celsius
                 'Bus index in electrical network': 3,
                 'Supplier max power': 500,  # kW
                 'Supplier min power': 0  # kW
                 },
                {'Group': 'Reefer group 2',
                 'Number of containers': 130,
                 'Mass of reefer content': 17000,  # kg per one container (avg)
                 'Heat capacity': 1347.7,  # J/(kg*Celsius)
                 'Surface area': 74.97,  # m^2
                 'Heat transition coefficient': 0.5,  # W/m^2Celsius
                 'Initial temperature': -4,  # degree Celsius
                 'Upper bound': -4,  # degree Celsius
                 'Lower bound': -6,  # degree Celsius
                 'Bus index in electrical network': 4,
                 'Supplier max power': 500,  # kW
                 'Supplier min power': 0  # kW
                 }
                ]

filename = "data/testcase/reefers_data.json"
with open(filename, 'w') as json_file:
    json.dump(reefers_data, json_file, indent=4)

# ======================================================================================================================
#   Vehicles data
# ======================================================================================================================
vehicles_data = {'Vehicles': [{'Name': 'Vehicle 1',
                               'Capacity of a battery': 21,
                               'Charging efficiency': 0.9,
                               'Discharging efficiency': 0.9,
                               'Maximum charging power': 5,
                               'Maximum discharging power': 5,
                               'Maximum SOC': 0.9,
                               'Minimum SOC': 0.1,
                               'Job plan': [{'Type of task': 'Charging',
                                             'Start': '2022-01-02 02:00:00',
                                             'Duration': {'hours': 5,
                                                          'minutes': 0,
                                                          'seconds': 0},
                                             'Initial SOC': 0.3,
                                             'Final SOC': 0.9,
                                             'Location': 'Charger 1'},
                                            {'Type of task': 'Operation',
                                             'Start': '2022-01-02 07:00:00',
                                             'Duration': {'hours': 12,
                                                          'minutes': 0,
                                                          'seconds': 0},
                                             'Initial SOC': 0.9,
                                             'Final SOC': 0.1,
                                             'Location': 'Port'},
                                            {'Type of task': 'Charging',
                                             'Start': '2022-01-02 19:00:00',
                                             'Duration': {'hours': 10,
                                                          'minutes': 0,
                                                          'seconds': 0},
                                             'Initial SOC': 0.1,
                                             'Final SOC': 0.9,
                                             'Location': 'Charger 2'}
                                            ]},
                              {'Name': 'Vehicle 2',
                               'Capacity of a battery': 16,
                               'Charging efficiency': 0.9,
                               'Discharging efficiency': 0.9,
                               'Maximum charging power': 4,
                               'Maximum discharging power': 4,
                               'Maximum SOC': 0.9,
                               'Minimum SOC': 0.1,
                               'Job plan': [{'Type of task': 'Charging',
                                             'Start': '2022-01-02 20:00:00',
                                             'Duration': {'hours': 7,
                                                          'minutes': 0,
                                                          'seconds': 0},
                                             'Initial SOC': 0.1,
                                             'Final SOC': 0.9,
                                             'Location': 'Charger 1'}
                                            ]}
                              ],
                 'Chargers': [{'Name': 'Charger 1',
                               'Bus index in electrical network': 3,
                               'Maximum power': 5,
                               'Minimum power': 0
                               },
                              {'Name': 'Charger 2',
                               'Bus index in electrical network': 3,
                               'Maximum power': 7,
                               'Minimum power': 0
                               }
                              ]}

filename = "data/testcase/vehicles_data.json"
with open(filename, 'w') as json_file:
    json.dump(vehicles_data, json_file, indent=4)
