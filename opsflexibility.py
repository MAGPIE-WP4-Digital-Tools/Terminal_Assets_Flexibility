class OPSFlexibility:
    def __init__(self, ship_name, ops_name):
        self.baseload_profile = dict()
        self.load_type = "OPS"
        self.ship_name = ship_name
        self.ops_name = ops_name
        self.flexibility_parameters = FlexibilityParameters()

    def define_baseload_profile(self, ops_baseload_profile, date_time):
        for t in sorted(set(ops_baseload_profile) & set(date_time)):
            self.baseload_profile[t] = ops_baseload_profile[t]

    def convert_to_dict(self):
        return {
            'baseload_profile': {dt.strftime('%Y-%m-%d %H:%M'): value for dt, value in self.baseload_profile.items()},
            'load_type': self.load_type,
            'ship_name': self.ship_name,
            'ops_name': self.ops_name,
            'flexibility_parameters': self.flexibility_parameters.convert_to_dict()
        }


# ======================================================================================================================
#   Class that contain Flexibility parameters
# ======================================================================================================================
class FlexibilityParameters:
    def __init__(self):
        self.upward_flex = dict()
        self.downward_flex = dict()
        self.minimum_energy = float()
        self.minimum_power = float()
        # self.time_interval = dict()
        # self.curt_cost = list()
        # self.shift_cost = list()

    def calculate_ops_flexibility_parameters(self, ship, ops, baseload_profile):
        self.minimum_power = ship.min_ops_power
        self.minimum_energy = ship.min_ops_energy * len(baseload_profile) / (ship.berth_time.seconds / 3600)
        for t in baseload_profile:
            min_1 = ops.max_OPS_power - baseload_profile[t]
            min_2 = ship.consumption[t] - baseload_profile[t]
            self.upward_flex[t] = min(min_1, min_2)
            self.downward_flex[t] = baseload_profile[t] - ship.min_ops_power

    def convert_to_dict(self):
        return {
            'upward_flex': {dt.strftime('%Y-%m-%d %H:%M'): value for dt, value in self.upward_flex.items()},
            'downward_flex': {dt.strftime('%Y-%m-%d %H:%M'): value for dt, value in self.downward_flex.items()},
            'minimum_energy': self.minimum_energy,
            'minimum_power': self.minimum_power
        }
