class OPS:
    def __init__(self):
        self.name = str()
        self.max_OPS_power = float()
        self.berth = str()
        self.bus_indx = int()
        self.supplied_ships = list()
        self.baseload_profile = dict()

    def extract_data_from_dict(self, ops_dict):
        self.name = ops_dict['Name']
        self.max_OPS_power = ops_dict['Maximum power']
        self.berth = ops_dict['Berth']
        self.bus_indx = ops_dict['Bus index in electrical network']

    def compute_ops_baseload_profile(self, ships):
        supplied_ships = list()
        baseload_profile = dict()
        for ship in ships:
            if self.berth == ship.allocated_berth:
                supplied_ships.append(ship.name)
                baseload_profile.update(ship.ops_baseload_profile)
        self.supplied_ships = supplied_ships
        self.baseload_profile = baseload_profile
