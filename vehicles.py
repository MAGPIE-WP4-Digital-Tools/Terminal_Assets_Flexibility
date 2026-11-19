import datetime


class Vehicle:
    def __init__(self):
        self.name = str()
        self.baseload = dict()
        self.SOC = dict()
        self.capacity = float()
        self.charging_efficiency = float()
        self.discharging_efficiency = float()
        self.max_charging = float()
        self.max_discharging = float()
        self.max_SOC = float()
        self.min_SOC = float()
        self.job_plan = list()

    def extract_data_from_dict(self, vehicle_dict):
        self.name = vehicle_dict['Name']
        self.capacity = vehicle_dict['Capacity of a battery']
        self.charging_efficiency = vehicle_dict['Charging efficiency']
        self.discharging_efficiency = vehicle_dict['Discharging efficiency']
        self.max_charging = vehicle_dict['Maximum charging power']
        self.max_discharging = vehicle_dict['Maximum discharging power']
        self.max_SOC = vehicle_dict['Maximum SOC']
        self.min_SOC = vehicle_dict['Minimum SOC']

    def extract_SOC_profile_from_jobs(self):
        for job in self.job_plan:
            self.SOC.update(job.SOC)


class VehicleJob:
    def __init__(self):
        self.type = str()
        self.baseload = dict()
        self.SOC = dict()
        self.start = datetime.datetime.now()
        self.duration = datetime.timedelta()
        self.initial_SOC = float()
        self.final_SOC = float()
        self.location = str()

    def extract_data_from_dict(self, vehicle_dict):
        self.type = vehicle_dict['Type of task']
        self.start = datetime.datetime.strptime(vehicle_dict['Start'], '%Y-%m-%d %H:%M:%S')
        self.duration = datetime.timedelta(hours=vehicle_dict['Duration']['hours'],
                                           minutes=vehicle_dict['Duration']['minutes'],
                                           seconds=vehicle_dict['Duration']['seconds'])
        self.initial_SOC = vehicle_dict['Initial SOC']
        self.final_SOC = vehicle_dict['Final SOC']
        self.location = vehicle_dict['Location']

    def compute_baseload_and_SOC_profiles(self, vehicle, chargers):
        capacity = vehicle.capacity
        eff_ch = vehicle.charging_efficiency
        job_duration = self.duration.seconds / 3600  # Convert to hours
        charger_assigned = self.location
        max_charging = 0
        for charger in chargers:
            if charger_assigned == charger.name:
                max_charging = min(vehicle.max_charging / eff_ch, charger.max_power)
        # Assumed a constant power consumption over the whole operation period
        if self.type == 'Operation':
            avg_SOC_decrease = (self.initial_SOC - self.final_SOC) / job_duration
            avg_power_consumption = avg_SOC_decrease * capacity
            for h in range(int(job_duration) + 1):
                time = self.start + datetime.timedelta(hours=h)
                if h != job_duration:
                    self.baseload[time] = avg_power_consumption
                self.SOC[time] = self.initial_SOC - h * avg_SOC_decrease

        # Assumed the maximum charging power until the full charging. After that charging power is equal to 0
        elif self.type == 'Charging':
            if max_charging * job_duration <= capacity:
                avg_SOC_increase = (self.initial_SOC - self.final_SOC) / job_duration
                time = self.start
                for h in range(int(job_duration)):
                    self.baseload[time] = max_charging
                    self.SOC[time] = self.initial_SOC - h * avg_SOC_increase
                    time = time + datetime.timedelta(hours=1)
                self.SOC[time] = self.final_SOC
            else:
                time = self.start
                self.SOC[time] = self.initial_SOC
                for h in range(int(job_duration)):
                    time = time + datetime.timedelta(hours=1)
                    self.SOC[time] = self.initial_SOC + (h + 1) * max_charging / capacity
                    if self.SOC[time] < self.final_SOC:
                        self.baseload[time - datetime.timedelta(hours=1)] = max_charging
                    else:
                        time_previous = time - datetime.timedelta(hours=1)
                        self.SOC[time] = self.final_SOC
                        self.baseload[time_previous] = (self.SOC[time] - self.SOC[time_previous]) * capacity


job_plan_example = {'self 1': [{'Start charging': datetime.datetime(2022, 1, 20, 10, 0, 0),
                                'End charging': datetime.datetime(2022, 1, 20, 11, 0, 0),
                                'Energy': 5,
                                'Initial SOC': 0.5},
                               {'Start charging': datetime.datetime(2022, 1, 20, 15, 0, 0),
                                'End charging': datetime.datetime(2022, 1, 20, 16, 2, 0),
                                'Energy': 10}],
                    'self 2': [{'Start charging': datetime.datetime(2022, 1, 20, 14, 0, 0),
                                'End charging': datetime.datetime(2022, 1, 20, 16, 0, 0),
                                'Energy': 20},
                               {'Start charging': datetime.datetime(2022, 1, 20, 21, 0, 0),
                                'End charging': datetime.datetime(2022, 1, 20, 22, 2, 0),
                                'Energy': 5}]
                    }
