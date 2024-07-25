from hypertiling.kernel.GRG import GenerativeReflectionGraph
from hqec.operator_push.tensor_toolbox import traverse_h_gate, ensure_minimum_legs, add_logical_legs, \
    create_topology_by_segments, swap_tensor_legs, get_tensor_from_id
from hqec.operator_push.network_toolbox import assign_layers_to_tensors, get_tensors_by_layer


def find_all_same_layer_neighbor_pairs(tensor_list):
    # Initialize a set to store unique neighbor pairs
    same_layer_neighbor_pairs = set()

    # Iterate through the tensor list
    for tensor in tensor_list:
        # Get the same-layer neighbors of the current tensor
        same_layer_tensor_ids = get_tensors_by_layer(tensor_list, tensor.layer)
        same_layer_neighbors = tensor.find_same_layer_neighbor(same_layer_tensor_ids)

        # Iterate through the same-layer neighbor list
        for neighbor_id in same_layer_neighbors:
            # Ensure the neighbor ID is greater than the current tensor ID to avoid duplicates
            if neighbor_id > tensor.tensor_id:
                # Create an ordered neighbor pair and add it to the set
                neighbor_pair = (tensor.tensor_id, neighbor_id)
            else:
                neighbor_pair = (neighbor_id, tensor.tensor_id)

            same_layer_neighbor_pairs.add(neighbor_pair)

    # Convert the set to a list and return
    return list(same_layer_neighbor_pairs)

# Assuming each tensor has a find_same_layer_neighbor method, and tensor_list is a list of all tensors
# Example usage:
# neighbor_pairs = find_all_same_layer_neighbor_pairs(tensor_list)


def find_split_tuples(tensor_tuples, split_numbers):
    # Sort the split numbers in descending order
    split_numbers_sorted = sorted(split_numbers, reverse=True)

    # Record split tuple pairs
    split_tuples = []

    # Iterate through each tuple pair
    for tensor_tuple in tensor_tuples:
        # Get the two tensor IDs of the current tuple
        tensor_id_1, tensor_id_2 = tensor_tuple

        # Initialize split interval indices
        split_index_1 = split_index_2 = None

        # Find the split intervals for each tensor ID
        for index, number in enumerate(split_numbers_sorted):
            if tensor_id_1 >= number:
                split_index_1 = index
                break
        for index, number in enumerate(split_numbers_sorted):
            if tensor_id_2 >= number:
                split_index_2 = index
                break

        # Check if the two tensor IDs are in different intervals
        if split_index_1 != split_index_2:
            # If they are not in the same interval, add the tuple pair to the split_tuples list
            split_tuples.append(tensor_tuple)

    return split_tuples

# Assuming tensor_tuples is the list obtained from the previous step (same_layer_neighbor_pairs list)
# split_numbers is a given list of numbers in descending order
# Example usage:
# split_tuples = find_split_tuples(neighbor_pairs, [20, 15, 10, 5])


def find_tensors_with_two_upper_neighbors(tensor_list):
    upper_neighbor_pairs = []

    # Iterate through the tensor list
    for tensor in tensor_list:
        upper_neighbors = []

        # Get the IDs of the neighbors of the current tensor
        neighbor_ids = tensor.get_connections()

        # Determine which neighbors are in the upper layer
        for neighbor_id in neighbor_ids:
            if tensor_list[neighbor_id].layer < tensor.layer:  # Neighbors in the upper layer
                upper_neighbors.append(neighbor_id)

        # If there are two upper layer neighbors, add them to the result list
        if len(upper_neighbors) == 2:
            # Sort by ID and create a tuple
            neighbor_pair = tuple(sorted(upper_neighbors))
            upper_neighbor_pairs.append(neighbor_pair)

    # Remove duplicate tuples
    unique_upper_neighbor_pairs = list(set(upper_neighbor_pairs))

    return unique_upper_neighbor_pairs

# Example usage:
# tensors_with_two_upper_neighbors = find_tensors_with_two_upper_neighbors(tensor_list)


def find_common_lower_layer_neighbors(tensor_pairs, tensor_list):
    common_neighbors = {}

    # Iterate through each tensor pair
    for tensor_id_1, tensor_id_2 in tensor_pairs:
        tensor_1_neighbors = set(tensor_list[tensor_id_1].get_connections())
        tensor_2_neighbors = set(tensor_list[tensor_id_2].get_connections())

        # Find common neighbors that are in the lower layer
        common = tensor_1_neighbors.intersection(tensor_2_neighbors)
        lower_layer_neighbors = [
            neighbor_id for neighbor_id in common
            if tensor_list[neighbor_id].layer > tensor_list[tensor_id_1].layer
        ]

        # If there are common lower layer neighbors, record them
        if lower_layer_neighbors:
            common_neighbors[(tensor_id_1, tensor_id_2)] = lower_layer_neighbors

    return common_neighbors

# Example usage:
# Given a list of tuples with tensor IDs
# tensor_pairs = [(tensor_id_1, tensor_id_2), (tensor_id_3, tensor_id_4), ...]

# tensor_list is a list of all Tensor objects
# common_lower_layer_neighbors = find_common_lower_layer_neighbors(tensor_pairs, tensor_list)


def setup_htn(l):
    # Define parameters
    p, q = 4, 5
    n = l + 1

    # Create a GenerativeReflectionGraph object
    grg = GenerativeReflectionGraph(p, q, n)

    # Create and connect tensors
    tensor_list = create_topology_by_segments(grg)

    # Ensure a minimum of 4 legs for tensors
    ensure_minimum_legs(tensor_list, 4, 0, len(tensor_list))

    # Add logical legs
    add_logical_legs(tensor_list, 0, len(tensor_list))

    # Add H Gate
    traverse_h_gate(tensor_list)

    # Assign layers to tensors
    assign_layers_to_tensors(tensor_list, 0)

    # Correct the leg order of same-layer tensors cut by a section line
    same_layer_neighbor_pairs = find_all_same_layer_neighbor_pairs(tensor_list)
    split_numbers = []
    n_tensor = len(tensor_list)
    max_layer = -1
    for tensor in tensor_list:
        if tensor.layer > max_layer:
            max_layer = tensor.layer
    neighbors_of_central_tensor = tensor_list[0].get_connections()
    for i, neighbors_id in enumerate(neighbors_of_central_tensor):
        split_numbers.append(neighbors_id)
    split_numbers.append(n_tensor + 1)
    split_tuples = find_split_tuples(same_layer_neighbor_pairs, split_numbers)
    if split_tuples:
        for split_tuple in split_tuples:
            tensor_id_0 = split_tuple[0]
            tensor_id_1 = split_tuple[1]
            tensor_0 = get_tensor_from_id(tensor_list, tensor_id_0)
            tensor_1 = get_tensor_from_id(tensor_list, tensor_id_1)
            if tensor_0.layer < max_layer:
                swap_tensor_legs(tensor_0, 1, 3, tensor_list)
                swap_tensor_legs(tensor_0, 2, 3, tensor_list)
                swap_tensor_legs(tensor_1, 1, 3, tensor_list)
                swap_tensor_legs(tensor_1, 2, 3, tensor_list)

    # Correct the leg order of tensors with 2 parent tensors cut by a section line
    two_parent_tensor_pairs = find_tensors_with_two_upper_neighbors(tensor_list)
    split_two_parent_tensor_pairs = find_split_tuples(two_parent_tensor_pairs, split_numbers)
    split_two_parent_tensor_pairs_to_children_tensor = find_common_lower_layer_neighbors(split_two_parent_tensor_pairs,
                                                                                         tensor_list)
    for children_tensor_id_list in split_two_parent_tensor_pairs_to_children_tensor.values():
        if children_tensor_id_list:
            children_tensor_id = children_tensor_id_list[0]
            children_tensor = get_tensor_from_id(tensor_list, children_tensor_id)
            if children_tensor.layer < max_layer:
                swap_tensor_legs(children_tensor, 1, 3, tensor_list)
                swap_tensor_legs(children_tensor, 2, 3, tensor_list)

    # Define UPS generators
    UPS1 = ['X', 'X', 'X', 'X', 'I']
    UPS2 = ['Z', 'I', 'Z', 'I', 'I']
    UPS3 = ['I', 'Z', 'I', 'Z', 'I']
    UPS4 = ['I', 'X', 'I', 'X', 'X']
    UPS5 = ['I', 'I', 'Z', 'Z', 'Z']

    # Assign UPS to tensors
    for tensor in tensor_list:
        tensor.ups_list = [UPS1, UPS2, UPS3, UPS4, UPS5]

        # Rule application
        neighbor_layers = [get_tensor_from_id(tensor_list, tensor_id).layer for tensor_id in tensor.get_connections()]
        current_layer = tensor.layer

        if all(neighbor_layer > current_layer for neighbor_layer in neighbor_layers):
            # Rule 1
            tensor.stabilizer_list = [UPS1, UPS2, UPS3]
            tensor.logical_z_list = [UPS5]
            tensor.logical_x_list = [UPS4]
        elif any(neighbor_layer < current_layer for neighbor_layer in neighbor_layers):
            upper_neighbors = [layer for layer in neighbor_layers if layer < current_layer]
            same_layer_neighbors = [layer for layer in neighbor_layers if layer == current_layer]
            if len(upper_neighbors) == 1 and len(same_layer_neighbors) == 0:
                # Rule 2
                tensor.stabilizer_list = [UPS3]
                tensor.logical_z_list = [UPS5]
                tensor.logical_x_list = [UPS4]
            elif len(upper_neighbors) == 2 and len(same_layer_neighbors) == 0:
                # Rule 4
                tensor.stabilizer_list = []
                tensor.logical_z_list = [UPS3]
                # Swap legs 1 and 4
                swap_tensor_legs(tensor, 1, 4, tensor_list)
                tensor.incomplete_logical = True
            else:
                # Rule 3
                tensor.stabilizer_list = []
                tensor.logical_z_list = [UPS5]
                tensor.logical_x_list = [UPS4]

    return tensor_list
