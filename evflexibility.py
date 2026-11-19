class EVFlexibility:
    def __init__(self, vehicle_name, charger_name, job_indx):
        self.baseload_profile = dict()
        self.load_type = "EV"
        self.vehicle_name = vehicle_name
        self.charger_name = charger_name
        self.job_indx = job_indx
        self.flexibility_parameters = FlexibilityParameters()

    def define_baseload_profile(self, job_baseload_profile, date_time):
        for t in sorted(set(job_baseload_profile) & set(date_time)):
            self.baseload_profile[t] = job_baseload_profile[t]

    def convert_to_dict(self):
        return {
            'baseload_profile': {dt.strftime('%Y-%m-%d %H:%M'): value for dt, value in self.baseload_profile.items()},
            'load_type': self.load_type,
            'vehicle_name': self.vehicle_name,
            'charger_name': self.charger_name,
            'job_indx': self.job_indx,
            'flexibility_parameters': self.flexibility_parameters.convert_to_dict()
        }

# ======================================================================================================================
#   Class that contain Flexibility parameters
# ======================================================================================================================
class FlexibilityParameters:
    def __init__(self):
        self.upward_flex = dict()
        self.downward_flex = dict()
        self.initial_SOC = float()
        self.final_SOC = float()
        self.charging_efficiency = float()
        self.discharging_efficiency = float()
        self.max_SOC = float()
        self.min_SOC = float()


    def calculate_ev_flexibility_parameters(self, vehicle, charger, job, baseload_profile):
        self.charging_efficiency = vehicle.charging_efficiency
        self.discharging_efficiency = vehicle.discharging_efficiency
        self.min_SOC = vehicle.min_SOC
        self.max_SOC = vehicle.max_SOC
        if list(job.baseload)[0] < list(baseload_profile)[0]:
            h = 0
            while list(job.baseload)[h] < list(baseload_profile)[0]:
                h += 1
            self.initial_SOC = job.initial_SOC + (job.final_SOC - job.initial_SOC) * h / len(job.baseload)
        else:
            self.initial_SOC = job.initial_SOC

        if list(job.baseload)[-1] > list(baseload_profile)[-1]:
            h = 0
            while list(job.baseload)[-1 - h] < list(baseload_profile)[-1]:
                h += 1
            self.final_SOC = job.final_SOC - (job.final_SOC - job.initial_SOC) * h / len(job.baseload)
        else:
            self.final_SOC = job.final_SOC
        for t in baseload_profile:
            min_1 = vehicle.max_charging / vehicle.charging_efficiency - baseload_profile[t]
            min_2 = charger.max_power - baseload_profile[t]
            self.upward_flex[t] = min(min_1, min_2)
            min_1 = baseload_profile[t] + vehicle.max_discharging / vehicle.discharging_efficiency
            min_2 = baseload_profile[t] - charger.min_power
            self.downward_flex[t] = min(min_1, min_2)

    def convert_to_dict(self):
        return {
            'upward_flex': {dt.strftime('%Y-%m-%d %H:%M'): value for dt, value in self.upward_flex.items()},
            'downward_flex': {dt.strftime('%Y-%m-%d %H:%M'): value for dt, value in self.downward_flex.items()},
            'initial_SOC': self.initial_SOC,
            'final_SOC': self.final_SOC,
            'charging_efficiency': self.charging_efficiency,
            'discharging_efficiency': self.discharging_efficiency,
            'max_SOC': self.max_SOC,
            'min_SOC': self.min_SOC
        }
