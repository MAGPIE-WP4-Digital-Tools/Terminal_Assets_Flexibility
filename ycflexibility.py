import datetime
from additional_functions import find_and_merge_by_key

class YCFlexibility:
    def __init__(self, yc_name, yc_baseload):
        self.baseload_profile = yc_baseload
        self.load_type = "YC"
        self.yard_crane_name = yc_name
        self.flexibility_parameters = FlexibilityParameters()

    def convert_to_dict(self):
        return {
            'baseload_profile': {dt.strftime('%Y-%m-%d %H:%M'): value for dt, value in self.baseload_profile.items()},
            'load_type': self.load_type,
            'yard_crane_name': self.yard_crane_name,
            'flexibility_parameters': self.flexibility_parameters.convert_to_dict()
        }


# ======================================================================================================================
#   Class that contain Flexibility parameters
# ======================================================================================================================
class FlexibilityParameters:
    def __init__(self):
        self.e_shift_loads = list()

    def calculate_yc_flexibility_parameters(self, crane, timesteps, time_delta):
        # The algorithm consists of two parts: iterating over each timestep, available_periods (perio
        for indx, timestep in enumerate(timesteps):
            if crane.baseload_profile[timestep] != 0:
                # Add possible shifting in forward direction (not possible for the last timestep)
                if timestep != timesteps[-1]:
                    available_periods = find_available_periods_in_forward_direction(timesteps, indx, crane, time_delta,
                                                                                    timestep)
                    add_shifting_intervals_in_forward_direction(available_periods, crane, timestep, self.e_shift_loads)
                # Add possible shifting in backward direction (not possible for the first timestep)
                if timestep != timesteps[0]:
                    available_periods = find_available_periods_in_backward_direction(timesteps, indx, crane, time_delta,
                                                                                    timestep)
                    add_shifting_intervals_in_backward_direction(available_periods, crane, timestep, self.e_shift_loads)

        # Merge shiftable intervals for similar job
        self.e_shift_loads = find_and_merge_by_key(self.e_shift_loads, 'id', 'shift_timesteps')

    def convert_to_dict(self):
        e_shift_loads_dict = list()
        for e_shift_load in self.e_shift_loads:
            e_shift_loads_dict.append({'id': e_shift_load['id'],
                                       'baseload_original_timestep': [dt.strftime('%Y-%m-%d %H:%M') for dt in
                                                                      e_shift_load['baseload_original_timestep']],
                                       'baseload_MW': e_shift_load['baseload_MW'],
                                       'shift_timesteps': [dt.strftime('%Y-%m-%d %H:%M') for dt in
                                                                      e_shift_load['shift_timesteps']]})
        return {
            'e_shift_loads': e_shift_loads_dict
        }


# ======================================================================================================================
#   Function to find shifting intervals in forward direction
# ======================================================================================================================
def find_available_periods_in_forward_direction(timesteps, indx, crane, time_delta, timestep):
    # Create a dict with all timesteps available for shifting with respective maximum power
    available_periods = dict()
    for timestep_forward in list(timesteps[indx + 1:]):
        if crane.baseload_profile[timestep_forward] == 0:
            available_periods[timestep_forward] = crane.max_power * time_delta.seconds / 3600
        else:
            job = crane.jobs_sorted[timestep_forward][0]
            if job.start < timestep_forward:
                if job.type == "Loading":
                    shift_till = job.end
                    max_shift = crane.max_power * (shift_till - timestep_forward).seconds / 3600
                    available_periods[timestep_forward] = max_shift
                    break

            for job in crane.jobs_sorted[timestep_forward][1:]:
                if job.type == 'Loading':
                    shift_till = job.end
                    max_shift = crane.max_power * (shift_till - timestep_forward).seconds / 3600
                    available_periods[timestep_forward] = max_shift
                    break
                elif job.type == 'Unloading':
                    shift_till = job.start
                    max_shift = crane.max_power * (shift_till - timestep_forward).seconds / 3600
                    available_periods[timestep_forward] = max_shift
                    break
            else:
                available_periods[timestep_forward] = crane.max_power * timestep.second / 3600
                continue
            break
    return available_periods

def add_shifting_intervals_in_forward_direction(available_periods, crane, timestep, e_shift_loads):
    # Add shiftable jobs
    for job in reversed(crane.jobs_sorted[timestep]):
        if job.end > timestep + datetime.timedelta(hours=1):
            shift_timesteps = []
            for period in available_periods:
                if ((period == timestep + datetime.timedelta(hours=1))
                        and (available_periods[period] >= job.energy *
                             ((timestep + datetime.timedelta(hours=1)) - job.start).seconds /
                             (job.end - job.start).seconds)):
                    shift_timesteps.append(period)
                    available_periods[period] += -(job.energy *
                                                   ((timestep + datetime.timedelta(hours=1)) -
                                                    job.start).seconds /
                                                   (job.end - job.start).seconds)
                elif available_periods[period] >= job.energy:
                    shift_timesteps.append(period)
                    available_periods[period] += -job.energy

            if len(shift_timesteps) != 0:
                e_shift_loads_i = dict()
                e_shift_loads_i["id"] = job.name
                e_shift_loads_i["baseload_original_timestep"] = [timestep,
                                                                 timestep + datetime.timedelta(hours=1)]
                e_shift_loads_i["baseload_MW"] = [
                    job.energy * (timestep + datetime.timedelta(hours=1) - job.start).seconds / (
                            job.end - job.start).seconds,
                    job.energy * (job.end - (timestep + datetime.timedelta(hours=1))).seconds / (
                            job.end - job.start).seconds]
                e_shift_loads_i["shift_timesteps"] = shift_timesteps
                e_shift_loads.append(e_shift_loads_i)
            if job.type == 'Loading':
                break
        elif job.start < timestep:
            break
        else:
            if job.type == 'Rearrangement':
                shift_timesteps = []
                for period in available_periods:
                    if available_periods[period] >= job.energy:
                        shift_timesteps.append(period)
                        available_periods[period] += -job.energy

                if len(shift_timesteps) != 0:
                    e_shift_loads_i = dict()
                    e_shift_loads_i["id"] = job.name
                    e_shift_loads_i["baseload_original_timestep"] = [timestep]
                    e_shift_loads_i["baseload_MW"] = [job.energy]
                    e_shift_loads_i["shift_timesteps"] = shift_timesteps
                    e_shift_loads.append(e_shift_loads_i)
            elif job.type == 'Loading':
                shift_timesteps = []
                for period in available_periods:
                    if available_periods[period] >= job.energy:
                        shift_timesteps.append(period)
                        available_periods[period] += -job.energy

                if len(shift_timesteps) != 0:
                    e_shift_loads_i = dict()
                    e_shift_loads_i["id"] = job.name
                    e_shift_loads_i["baseload_original_timestep"] = [timestep]
                    e_shift_loads_i["baseload_MW"] = [job.energy]
                    e_shift_loads_i["shift_timesteps"] = shift_timesteps
                    e_shift_loads.append(e_shift_loads_i)
                break
            else:
                break


# ======================================================================================================================
#    Function to find shifting intervals in backward direction
# ======================================================================================================================
def find_available_periods_in_backward_direction(timesteps, indx, crane, time_delta, timestep):
    # Create a dict with all timesteps available for shifting with respective maximum power
    available_periods = dict()
    for timestep_backward in reversed(list(timesteps[:indx])):
        if crane.baseload_profile[timestep_backward] == 0:
            available_periods[timestep_backward] = crane.max_power * time_delta.seconds / 3600
        else:
            job = crane.jobs_sorted[timestep_backward][-1]
            if job.end > timestep_backward + datetime.timedelta(hours=1):
                if job.type == "Unloading":
                    shift_till = job.start
                    max_shift = crane.max_power * (shift_till - timestep_backward).seconds / 3600
                    available_periods[timestep_backward] = max_shift
                    break

            for job in reversed(crane.jobs_sorted[timestep_backward][:-1]):
                if job.type == 'Loading':
                    shift_till = job.end
                    max_shift = crane.max_power * (timestep_backward +
                                                   datetime.timedelta(
                                                       hours=1) - shift_till).seconds / 3600
                    available_periods[timestep_backward] = max_shift
                    break
                elif job.type == 'Unloading':
                    shift_till = job.start
                    max_shift = crane.max_power * (timestep_backward +
                                                   datetime.timedelta(
                                                       hours=1) - shift_till).seconds / 3600
                    available_periods[timestep_backward] = max_shift
                    break
            else:
                available_periods[timestep_backward] = crane.max_power * timestep.seconds / 3600
                continue
            break
    return available_periods

def add_shifting_intervals_in_backward_direction(available_periods, crane, timestep, e_shift_loads):
    # Add shiftable jobs
    for job in crane.jobs_sorted[timestep]:
        if job.start < timestep:
            shift_timesteps = []
            for period in available_periods:
                if ((period == timestep - datetime.timedelta(hours=1))
                        and (available_periods[period] >= job.energy * ((job.end - timestep).seconds /
                                                                        (
                                                                                job.end - job.start).seconds))):
                    shift_timesteps.append(period)
                    available_periods[period] += -job.energy * ((job.end - timestep).seconds /
                                                                (job.end - job.start).seconds)
                elif available_periods[period] >= job.energy:
                    shift_timesteps.append(period)
                    available_periods[period] += -job.energy

            if len(shift_timesteps) != 0:
                e_shift_loads_i = dict()
                e_shift_loads_i["id"] = job.name
                e_shift_loads_i["baseload_original_timestep"] = [timestep - datetime.timedelta(hours=1),
                                                                 timestep]
                e_shift_loads_i["baseload_MW"] = [
                    job.energy * (timestep - job.start).seconds / (job.end - job.start).seconds,
                    job.energy * (job.end - timestep).seconds / (job.end - job.start).seconds]
                e_shift_loads_i["shift_timesteps"] = shift_timesteps
                e_shift_loads.append(e_shift_loads_i)
            if job.type == 'Unloading':
                break
        elif job.end > timestep + datetime.timedelta(hours=1):
            break
        else:
            if job.type == 'Rearrangement':
                shift_timesteps = []
                for period in available_periods:
                    if available_periods[period] >= job.energy:
                        shift_timesteps.append(period)
                        available_periods[period] += -job.energy

                if len(shift_timesteps) != 0:
                    e_shift_loads_i = dict()
                    e_shift_loads_i["id"] = job.name
                    e_shift_loads_i["baseload_original_timestep"] = [timestep]
                    e_shift_loads_i["baseload_MW"] = [job.energy]
                    e_shift_loads_i["shift_timesteps"] = shift_timesteps
                    e_shift_loads.append(e_shift_loads_i)
            elif job.type == 'Unloading':
                shift_timesteps = []
                for period in available_periods:
                    if available_periods[period] >= job.energy:
                        shift_timesteps.append(period)
                        available_periods[period] += -job.energy

                if len(shift_timesteps) != 0:
                    e_shift_loads_i = dict()
                    e_shift_loads_i["id"] = job.name
                    e_shift_loads_i["baseload_original_timestep"] = [timestep]
                    e_shift_loads_i["baseload_MW"] = [job.energy]
                    e_shift_loads_i["shift_timesteps"] = shift_timesteps
                    e_shift_loads.append(e_shift_loads_i)
                break
            else:
                break
