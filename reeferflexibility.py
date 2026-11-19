import math

class ReeferFlexibility:
    def __init__(self, reefer_group_name):
        self.baseload_profile = dict()
        self.load_type = "Reefer"
        self.reefer_group_name = reefer_group_name
        self.flexibility_parameters = FlexibilityParameters()

    def define_baseload_profile(self, reefer_baseload_profile, date_time):
        for t in sorted(set(reefer_baseload_profile) & set(date_time)):
            self.baseload_profile[t] = reefer_baseload_profile[t]

    def convert_to_dict(self):
        return {
            'baseload_profile': {dt.strftime('%Y-%m-%d %H:%M'): value for dt, value in self.baseload_profile.items()},
            'load_type': self.load_type,
            'reefer_group_name': self.reefer_group_name,
            'flexibility_parameters': self.flexibility_parameters.convert_to_dict()
        }


# ======================================================================================================================
#   Class that contain Flexibility parameters
# ======================================================================================================================
class FlexibilityParameters:
    def __init__(self):
        self.initial_temperature = float()
        self.max_temperature = float()
        self.min_temperature = float()
        self.max_power = float()
        self.min_power = float()
        self.c1 = float()
        self.c2 = float()
        self.c3 = dict()


    def calculate_reefer_flexibility_parameters(self, reefer, ambient_temperature):
        self.initial_temperature = reefer.initial_temperature
        self.max_temperature = reefer.upper_bound
        self.min_temperature = reefer.lower_bound
        self.max_power = reefer.max_power
        self.min_power = reefer.min_power
        m = reefer.content_mass * reefer.number_of_containers
        c = reefer.heat_capacity
        A = reefer.area * reefer.number_of_containers
        k = reefer.heat_transition_coefficient
        self.c1 = math.exp(-A * k / m / c)
        self.c2 = 1 / m / c
        for t in ambient_temperature:
            self.c3[t] = (ambient_temperature[t]) * (1 - math.exp(-A * k / m / c))

    def convert_to_dict(self):
        return {
            'initial_temperature': self.initial_temperature,
            'max_temperature': self.max_temperature,
            'min_temperature': self.min_temperature,
            'max_power': self.max_power,
            'min_power': self.min_power,
            'c1': self.c1,
            'c2': self.c2,
            'c3': {dt.strftime('%Y-%m-%d %H:%M'): value for dt, value in self.c3.items()}
        }