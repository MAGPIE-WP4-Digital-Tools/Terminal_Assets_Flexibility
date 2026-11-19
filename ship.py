import datetime


class Ship:
    def __init__(self):
        self.name = str()
        self.allocated_berth = str()
        self.arrival = datetime.time(0, 0)
        self.berth_time = datetime.timedelta()
        self.min_ops_energy = float()
        self.consumption = dict()
        self.ops_baseload_profile = dict()

        # Additional data that could be required in the future
        self.auxiliary_engine_max_power = float()
        self.min_ops_power = float()
        self.ops_energy_penalization = float()
        self.ops_power_penalization = float()

    def extract_data_from_dict(self, ship_dict):
        self.name = ship_dict['Name']
        self.allocated_berth = ship_dict['Allocated berth']
        self.arrival = ship_dict['Arrival time']
        self.berth_time = ship_dict['Berth time']
        self.min_ops_energy = ship_dict['Minimum OPS energy']
        for indx, t in enumerate(range(int(self.berth_time.seconds/3600))):
            timestep = self.arrival + datetime.timedelta(hours=t)
            self.consumption[timestep] = ship_dict['Power consumption'][indx]

    def compute_ship_baseload_profile(self):
        berth_time_hours = self.berth_time.seconds / 3600
        power = self.min_ops_energy / berth_time_hours
        ship_baseload_profile = dict()
        time = self.arrival
        for h in range(int(berth_time_hours)):
            ship_baseload_profile[time] = power
            time = time + datetime.timedelta(hours=1)
        self.ops_baseload_profile = ship_baseload_profile


berth_plan_example = {'Berth 1': [{'Ship': 'Ship 1',
                                   'Arrival time': datetime.datetime(2022, 1, 20, 10, 0, 0),
                                   'Minimum berth time': datetime.timedelta(hours=8),
                                   'Minimum OPS energy': 5,
                                   'OPS penalization': 100,
                                   'Consumption': [10, 10, 5, 5, 5, 5, 5, 5]},
                                  {'Ship': 'Ship 2',
                                   'Arrival time': datetime.datetime(2022, 1, 20, 20, 0, 0),
                                   'Minimum berth time': datetime.timedelta(hours=3),
                                   'Minimum OPS energy': 5,
                                   'OPS penalization': 100,
                                   'Consumption': [7, 7, 7]}],

                      'Berth 2': [{'Ship': 'Ship 3',
                                   'Arrival time': datetime.datetime(2022, 1, 20, 8, 0, 0),
                                   'Minimum berth time': datetime.timedelta(hours=7),
                                   'Minimum OPS energy': 5,
                                   'OPS penalization': 100,
                                   'Consumption': [6, 6, 8, 8, 8, 8, 8]}]
                      }
