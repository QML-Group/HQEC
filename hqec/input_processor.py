import csv


def process_quantum_csv(file_path):
    """
    Process a CSV file containing tensor IDs and their corresponding operators.

    Args:
    file_path (str): The path to the CSV file.

    Returns:
    dict: A dictionary with tensor IDs as keys and a dictionary of operators as values.
    """
    tensor_dict = {}

    with open(file_path, newline='') as csvfile:
        csv_reader = csv.reader(csvfile)
        for row in csv_reader:
            tensor_id = row[0]
            operators = {}

            for operator in row[1:]:
                op_type, op_value = operator.split('=')
                operators[op_type.strip()] = op_value.strip()

            tensor_dict[tensor_id] = operators

    return tensor_dict

# Example usage
# Note: The actual file path should be provided here
# file_path = 'path_to_your_csv_file.csv'
# tensor_data = process_quantum_csv(file_path)
# print(tensor_data)


def collect_stabilizers(tensor_dict):
    """
    Collect all stabilizers from a dictionary of tensors.

    Args:
    tensor_dict (dict): A dictionary with tensor IDs as keys and a dictionary of operators as values.

    Returns:
    list: A list of all stabilizers across all tensors.
    """
    stabilizers = []

    for operators in tensor_dict.values():
        for op_type, op_value in operators.items():
            if 'stabilizer' in op_type:
                stabilizers.append(op_value)

    return stabilizers

# Example usage
# Assuming tensor_data is the dictionary obtained from the process_quantum_csv function
# stabilizers = collect_stabilizers(tensor_data)
# print(stabilizers)


def collect_logical_zs(tensor_dict):
    """
    Collect all stabilizers from a dictionary of tensors.

    Args:
    tensor_dict (dict): A dictionary with tensor IDs as keys and a dictionary of operators as values.

    Returns:
    list: A list of all logical zs across all tensors.
    """
    logical_zs = []

    for operators in tensor_dict.values():
        for op_type, op_value in operators.items():
            if 'logical_z' in op_type:
                logical_zs.append(op_value)

    return logical_zs

# Example usage
# Assuming tensor_data is the dictionary obtained from the process_quantum_csv function
# logical_zs = collect_logical_zs(tensor_data)
# print(logical_zs)


def collect_logical_xs(tensor_dict):
    """
    Collect all stabilizers from a dictionary of tensors.

    Args:
    tensor_dict (dict): A dictionary with tensor IDs as keys and a dictionary of operators as values.

    Returns:
    list: A list of all logical xs across all tensors.
    """
    logical_xs = []

    for operators in tensor_dict.values():
        for op_type, op_value in operators.items():
            if 'logical_x' in op_type:
                logical_xs.append(op_value)

    return logical_xs

# Example usage
# Assuming tensor_data is the dictionary obtained from the process_quantum_csv function
# logical_xs = collect_logical_xs(tensor_data)
# print(logical_xs)


def read_tensor_layers_from_csv(file_path):
    """
    Read a CSV file and return a dictionary mapping tensor IDs to layer numbers.

    Args:
    file_path (str): Path to the CSV file.

    Returns:
    dict: A dictionary where keys are tensor IDs and values are layer numbers.
    """
    tensor_layers = {}

    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row
        for row in reader:
            tensor_id, layer_number = row
            tensor_layers[int(tensor_id)] = int(layer_number)

    return tensor_layers

# Example usage
# file_path = 'path_to_your_csv_file.csv'
# tensor_layers = read_tensor_layers_from_csv(file_path)
# print(tensor_layers)


def get_formatted_ups_and_stabilizers(tensor_info, tensor_id):
    if tensor_id not in tensor_info:
        print(f"Tensor ID {tensor_id} not found.")
        return None

    ups_list = tensor_info[tensor_id]["ups_list"]
    stabilizer_list = tensor_info[tensor_id]["stabilizer_list"]

    formatted_ups_list = [''.join(ups) for ups in ups_list]
    formatted_stabilizer_list = [''.join(stabilizer) for stabilizer in stabilizer_list]

    return formatted_ups_list, formatted_stabilizer_list

# Example usage:
# Assuming tensor_info_dict is the output from the extract_tensor_info function
# formatted_ups, formatted_stabilizers = get_formatted_ups_and_stabilizers(tensor_info_dict, some_tensor_id)


def extract_stabilizers_from_result_dict(result_dict):
    """
    Extract all stabilizers from a result dictionary and return them as a list.

    Args:
    result_dict (dict): A dictionary containing stabilizers.

    Returns:
    list: A list of all stabilizers found in the dictionary.
    """
    stabilizers_list = []
    for key in result_dict:
        if 'stabilizers' in result_dict[key]:
            stabilizers = result_dict[key]['stabilizers']
            stabilizers_list.extend(stabilizers.values())

    return stabilizers_list


def extract_logicals_from_result_dict(result_dict):
    """
    Extract all stabilizers from a result dictionary and return them as a list.

    Args:
    result_dict (dict): A dictionary containing stabilizers.

    Returns:
    list: A list of all stabilizers found in the dictionary.
    """
    logical_xs = []
    logical_zs = []
    for key in result_dict:
        if 'logical_x' in result_dict[key]:
            logical_x = result_dict[key]['logical_x']
            logical_xs.extend(logical_x.values())
        if 'logical_z' in result_dict[key]:
            logical_z = result_dict[key]['logical_z']
            logical_zs.extend(logical_z.values())

    return logical_zs, logical_xs
