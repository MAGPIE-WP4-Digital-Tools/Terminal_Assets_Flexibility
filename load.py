import datetime
from ops import OPS
from inputdata import InputData
import math
from collections import defaultdict
from additional_functions import *
from opsflexibility import OPSFlexibility
from ycflexibility import YCFlexibility
from evflexibility import EVFlexibility
from reeferflexibility import ReeferFlexibility


class BusLoad:
    def __init__(self, node, input_data):
        self.bus_indx = int(node)
        self.number_of_intervals = len(input_data.date_time)
        self.timestep = input_data.timestep
        self.date_time = input_data.date_time
        self.flexible_load = list()

    def calculate_flexible_loads(self, input_data):
        _calculate_flexible_loads(self, input_data)

    def convert_to_dict(self):
        return {
            'bus_indx': self.bus_indx,
            'number_of_intervals': self.number_of_intervals,
            'timestep': str(self.timestep),
            'date_time': [dt.strftime('%Y-%m-%d %H:%M') for dt in self.date_time],
            'flexible_load': [flexible_load.convert_to_dict() for flexible_load in self.flexible_load]
        }


# ======================================================================================================================
#   Functions to initiate Loads
# ======================================================================================================================
def _calculate_flexible_loads(load, input_data):
    # OPS flexibility
    for ops in input_data.OPSs:
        if load.bus_indx == ops.bus_indx:
            for ship in input_data.berth_plan:
                ship_at_berth_time = list(ship.ops_baseload_profile)
                calc_period = load.date_time
                if (ship.name in ops.supplied_ships) and check_overlapping(ship_at_berth_time, calc_period):
                    flexible_load = OPSFlexibility(ship.name, ops.name)
                    flexible_load.define_baseload_profile(ship.ops_baseload_profile, load.date_time)
                    flexible_load.flexibility_parameters.calculate_ops_flexibility_parameters(ship, ops, flexible_load.baseload_profile)
                    load.flexible_load.append(flexible_load)

    # YC flexibility
    for crane in input_data.cranes:
        if (load.bus_indx == crane.bus_indx) and (sum(crane.baseload_profile.values()) != 0):
            flexible_load = YCFlexibility(crane.name, crane.baseload_profile)
            # Finish function definition
            flexible_load.flexibility_parameters.calculate_yc_flexibility_parameters(crane, load.date_time, load.timestep)
            load.flexible_load.append(flexible_load)

    # EV flexibility
    for charger in input_data.chargers:
        if load.bus_indx == charger.bus_indx:
            for vehicle in input_data.vehicles:
                indx = 0
                for job in vehicle.job_plan:
                    charging_time = list(job.baseload)
                    calc_period = load.date_time
                    if job.location == charger.name and check_overlapping(charging_time, calc_period):
                        flexible_load = EVFlexibility(vehicle.name, charger.name, indx)
                        flexible_load.define_baseload_profile(job.baseload, calc_period)
                        flexible_load.flexibility_parameters.calculate_ev_flexibility_parameters(vehicle, charger, job,
                                                                                                 flexible_load.baseload_profile)
                        load.flexible_load.append(flexible_load)
                    indx += 1

    # Reefer flexibility
    for reefer in input_data.reefers:
        if load.bus_indx == reefer.bus_indx:
            flexible_load = ReeferFlexibility(reefer.group_name)
            flexible_load.define_baseload_profile(reefer.baseload_profile, load.date_time)
            flexible_load.flexibility_parameters.calculate_reefer_flexibility_parameters(reefer,
                                                                                         input_data.ambient_temperature)
            load.flexible_load.append(flexible_load)
