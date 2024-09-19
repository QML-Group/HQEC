from OperatorPush.TensorToolbox import get_tensor_from_id, connect_tensors, swap_tensor_legs
from collections import deque


def create_layer_q4(tensor_list, previous_layer_id_list, legs_per_tensor):
    # Create a mapping for the tensor connections
    tensor_connections = {}
    start_id = previous_layer_id_list[-1] + 1
    target_id = start_id - 1
    tensor_id_of_this_layer = []

    # The central tensor connects to 'legs_per_tensor' other tensors
    if len(previous_layer_id_list) == 1:
        for i in range(legs_per_tensor):
            target_id = start_id + i
            tensor_connections[(previous_layer_id_list[0], target_id)] = True
            if target_id not in tensor_id_of_this_layer:
                tensor_id_of_this_layer.append(target_id)
        # Execute the connections
        for (tensor_a, tensor_b) in tensor_connections:
            connect_tensors(tensor_list, tensor_a, tensor_b)
    else:
        for i, previous_layer_tensor_id in enumerate(previous_layer_id_list):
            last_tensor = False
            if i == len(previous_layer_id_list) - 1:
                last_tensor = True
            current_previous_layer_tensor = get_tensor_from_id(tensor_list, previous_layer_tensor_id)
            legs_number_left_for_current_tensor = legs_per_tensor - len(current_previous_layer_tensor.get_connections())
            loop_num = legs_number_left_for_current_tensor
            if last_tensor:
                loop_num -= 1
            for j in range(loop_num):
                target_id += 1
                tensor_connections[(previous_layer_tensor_id, target_id)] = True
                if target_id not in tensor_id_of_this_layer:
                    tensor_id_of_this_layer.append(target_id)
            if last_tensor:
                tensor_connections[(previous_layer_tensor_id, start_id)] = True
            target_id -= 1
        # Execute the connections
        for (tensor_a, tensor_b) in tensor_connections:
            connect_tensors(tensor_list, tensor_a, tensor_b)

        # Swap leg 0 and 1 for the first tensor of this layer
        first_tensor_id_of_this_layer = tensor_id_of_this_layer[0]
        print(first_tensor_id_of_this_layer)
        first_tensor_of_this_layer = get_tensor_from_id(tensor_list, first_tensor_id_of_this_layer)
        swap_tensor_legs(first_tensor_of_this_layer, 0, 1, tensor_list)
    return tensor_id_of_this_layer


def assign_layers_to_tensors(tensor_list, center_tensor_id=0):
    # Initialize all tensors with an undefined layer (-1)
    for tensor in tensor_list:
        tensor.layer = -1

    # Create a queue for BFS and add the center tensor
    queue = deque([center_tensor_id])

    # The center tensor is at layer 0
    tensor_list[center_tensor_id].layer = 0

    # Perform BFS to set layers
    while queue:
        current_tensor_id = queue.popleft()
        current_tensor = get_tensor_from_id(tensor_list, current_tensor_id)
        current_layer = current_tensor.layer

        # Iterate through all the connected tensors
        for neighbor_id in current_tensor.get_connections():
            neighbor_tensor = get_tensor_from_id(tensor_list, neighbor_id)

            # If the neighbor hasn't been assigned a layer yet
            if neighbor_tensor.layer == -1:
                # Assign the neighbor a layer (current layer + 1)
                neighbor_tensor.layer = current_layer + 1
                # Add the neighbor to the queue for further processing
                queue.append(neighbor_id)

# Assuming each tensor has a .get_connections() method that returns the list of connected tensor IDs
# Example usage:
# assign_layers_to_tensors(tensor_list, center_tensor_id=0)


def get_tensors_by_layer(tensor_list, layer_number):
    # Initialize a list to collect tensor IDs at the specified layer
    tensor_ids_at_layer = []

    # Iterate through the list of tensors and check the layer information for each tensor
    for tensor in tensor_list:
        if tensor.layer == layer_number:
            tensor_ids_at_layer.append(tensor.tensor_id)

    # Return the collected list of tensor IDs
    return tensor_ids_at_layer

# Assuming each tensor object has a .layer attribute
# Example usage:
# tensor_ids_layer_n = get_tensors_by_layer(tensor_list, n)
