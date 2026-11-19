import math


class Reefer:
    def __init__(self):
        self.group_name = str()
        self.number_of_containers = int()
        self.bus_indx = int()
        self.content_mass = float()
        self.heat_capacity = float()  # kWh/(kg*Celsius)
        self.area = float()
        self.heat_transition_coefficient = float()  # kW/m^2Celsius
        self.initial_temperature = float()
        self.upper_bound = float()
        self.lower_bound = float()
        self.internal_temperature = dict()
        self.baseload_profile = dict()
        self.max_power = float()
        self.min_power = float()

    def extract_data_from_dict(self, reefer_group_dict):
        self.group_name = reefer_group_dict['Group']
        self.number_of_containers = reefer_group_dict['Number of containers']
        self.bus_indx = reefer_group_dict['Bus index in electrical network']
        self.content_mass = reefer_group_dict['Mass of reefer content']
        self.heat_capacity = reefer_group_dict['Heat capacity'] / (3600 * 1000)  # Convert to kWh/(kg*Celsius)
        self.area = reefer_group_dict['Surface area']
        self.heat_transition_coefficient = reefer_group_dict[
                                                 'Heat transition coefficient'] / 1000  # Convert to kW/m^2Celsius
        self.initial_temperature = reefer_group_dict['Initial temperature']
        self.upper_bound = reefer_group_dict['Upper bound']
        self.lower_bound = reefer_group_dict['Lower bound']
        self.max_power = reefer_group_dict['Supplier max power']
        self.min_power = reefer_group_dict['Supplier min power']

    def compute_baseload_and_internal_temperature(self, ambient_temperature, timestep):
        # ASSUMPTIONS
        # - The control algorithm aims to minimize power consumption. It means that the container is cooled only if the
        # internal temperature is equal to the upper bound.
        # - The ambient temperature cannot be lower than the lower bound of the internal container temperature. Without
        # this assumption, reefer containers must be heated
        m = self.content_mass * self.number_of_containers
        c = self.heat_capacity
        A = self.area * self.number_of_containers
        k = self.heat_transition_coefficient
        delta_t = timestep.seconds / 3600  # Convert to h
        internal_temperature = dict()
        cooling_power = dict()
        for indx, time in enumerate(ambient_temperature):
            if indx == 0:
                internal_temperature[time] = self.initial_temperature

            elif indx != len(ambient_temperature) - 1:
                # Internal temperature that is free from regulation
                internal_temperature_free = internal_temperature[time - timestep] + \
                                            (ambient_temperature[time - timestep] -
                                             internal_temperature[time - timestep]) * \
                                            (1 - math.exp(-A * k / m / c * delta_t))

                # If the internal temperature without a regulation exceeds the upper bound, the internal temperature is
                # set to be equal to the upper bound, and the cooling power to maintain this temperature is calculated
                if internal_temperature_free >= self.upper_bound:
                    internal_temperature[time] = self.upper_bound
                    cooling_power[time - timestep] = m * c / delta_t * (
                            internal_temperature[time - timestep] - internal_temperature[time] +
                            (ambient_temperature[time - timestep] - internal_temperature[time - timestep]) *
                            (1 - math.exp(-A * k / m / c * delta_t)))

                # Otherwise, the internal temperature is set to be equal to the temperature without a regulation, and
                # the cooling power in the previous time step is set to be 0
                else:
                    internal_temperature[time] = internal_temperature_free
                    cooling_power[time - timestep] = 0

            else:
                # For the last timestep, it is assumed that temperature for the next time step unchanged (
                # ambient_temperature[time - timestep] appears ambient_temperature[time])
                #
                # Internal temperature that is free from regulation
                internal_temperature_free = internal_temperature[time - timestep] + \
                                            (ambient_temperature[time] -
                                             internal_temperature[time - timestep]) * \
                                            (1 - math.exp(-A * k / m / c * delta_t))

                # If the internal temperature without a regulation exceeds the upper bound, the internal temperature is
                # set to be equal to the upper bound, and the cooling power to maintain this temperature is calculated
                if internal_temperature_free >= self.upper_bound:
                    internal_temperature[time] = self.upper_bound
                    cooling_power[time - timestep] = m * c / delta_t * (
                            internal_temperature[time - timestep] - internal_temperature[time] +
                            (ambient_temperature[time] - internal_temperature[time - timestep]) *
                            (1 - math.exp(-A * k / m / c * delta_t)))

                # Otherwise, the internal temperature is set to be equal to the temperature without a regulation, and
                # the cooling power in the previous time step is set to be 0
                else:
                    internal_temperature[time] = internal_temperature_free
                    cooling_power[time - timestep] = 0

        self.internal_temperature = internal_temperature
        self.baseload_profile = cooling_power
