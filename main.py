from inputdata import InputData
from load import BusLoad
import os
import json

if __name__ == '__main__':
    # Define case name
    case = 'testcase'
    # Read input data
    input_data = InputData()
    input_data.read_input_data(case)
    input_data.preprocessing_input_data()

    # Compute flexibility parameters and convert it to dictionary
    nodal_load = list()
    nodal_load_dict = dict()
    for node in input_data.nodes:
        load = BusLoad(node, input_data)  # Create object of class Load for current node
        load.calculate_flexible_loads(input_data)
        nodal_load.append(load)
        nodal_load_dict[node] = load.convert_to_dict()

    # Save to JSON
    filename = os.path.join('data', f'{case}_results.json')
    with open(filename, 'w') as file:
        json.dump(nodal_load_dict, file, ensure_ascii=False, indent=4)
    print(1)


