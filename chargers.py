
class Charger:
    def __init__(self):
        self.name = str()
        self.bus_indx = int()
        self.max_power = float()
        self.min_power = float()
        
    def extract_data_from_dict(self, charger_dict):
        self.name = charger_dict['Name']
        self.bus_indx = charger_dict['Bus index in electrical network']
        self.max_power = charger_dict['Maximum power']
        self.min_power = charger_dict['Minimum power']