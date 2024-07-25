from hqec.operator_push.network_toolbox import create_layer_q4, assign_layers_to_tensors
from hqec.operator_push.tensor_toolbox import ensure_minimum_legs, add_logical_legs, get_tensor_from_id


def setup_zero_rate_happy(R):
    if type(R) is not int:
        raise ValueError("R is not int")
    elif R <= 0:
        raise ValueError("R <= 0 is not allowed")
    tensor_list = []
    layer_list = []
    if R == 1:
        r1 = create_layer_q4(tensor_list, [0], 5)
        layer_list.append(r1)
    else:
        r1 = create_layer_q4(tensor_list, [0], 5)
        layer_list.append(r1)
        for i, R_num in enumerate(range(2, R + 1)):
            temp = create_layer_q4(tensor_list, layer_list[i], 6)
            layer_list.append(temp)

    # Ensure Minimum Legs to 5 for tensor 0
    ensure_minimum_legs(tensor_list, 5, 0, 1)

    # Ensure Minimum Legs to 6 for other tensors
    ensure_minimum_legs(tensor_list, 6, 1, len(tensor_list))

    # Add Logical
    add_logical_legs(tensor_list, 0, 1)

    # Assign layer
    assign_layers_to_tensors(tensor_list, 0)

    # Define UPS generators
    UPSa1 = ['X', 'Z', 'Z', 'X', 'I', 'I']
    UPSa2 = ['I', 'X', 'Z', 'Z', 'X', 'I']
    UPSa3 = ['X', 'I', 'X', 'Z', 'Z', 'I']
    UPSa4 = ['Z', 'X', 'I', 'X', 'Z', 'I']
    UPSa5 = ['X', 'X', 'X', 'X', 'X', 'X']
    UPSa6 = ['Z', 'Z', 'Z', 'Z', 'Z', 'Z']

    UPSb1 = ['I', 'X', 'Z', 'Z', 'X', 'I']
    UPSb2 = ['I', 'I', 'X', 'Z', 'Z', 'X']
    UPSb3 = ['I', 'X', 'I', 'X', 'Z', 'Z']
    UPSb4 = ['I', 'Z', 'X', 'I', 'X', 'Z']
    UPSb5 = ['X', 'X', 'X', 'X', 'X', 'X']
    UPSb6 = ['Z', 'Z', 'Z', 'Z', 'Z', 'Z']

    UPSc1 = ['I', 'I', 'X', 'Z', 'Z', 'X']
    UPSc2 = ['I', 'I', 'Y', 'X', 'X', 'Y']
    UPSc3 = ['I', 'X', 'I', 'Z', 'X', 'Z']
    UPSc4 = ['I', 'Z', 'X', 'X', 'I', 'Z']
    UPSc5 = ['X', 'I', 'Z', 'Z', 'X', 'I']
    UPSc6 = ['Z', 'I', 'Z', 'X', 'I', 'X']


    # Assign UPS to tensors
    for tensor in tensor_list:

        # Rule application
        neighbor_layers = [get_tensor_from_id(tensor_list, tensor_id).layer for tensor_id in tensor.get_connections()]
        current_layer = tensor.layer

        if all(neighbor_layer > current_layer for neighbor_layer in neighbor_layers):
            # Rule 1
            tensor.ups_list = [UPSa1, UPSa2, UPSa3, UPSa4, UPSa5, UPSa6]
            tensor.stabilizer_list = [UPSa1, UPSa2, UPSa3, UPSa4]
            tensor.logical_z_list = [UPSa6]
            tensor.logical_x_list = [UPSa5]
        elif any(neighbor_layer < current_layer for neighbor_layer in neighbor_layers):
            upper_neighbors = [layer for layer in neighbor_layers if layer < current_layer]
            if len(upper_neighbors) == 1:
                # Rule 2
                tensor.ups_list = [UPSb1, UPSb2, UPSb3, UPSb4, UPSb5, UPSb6]
                tensor.stabilizer_list = [UPSb1, UPSb2, UPSb3, UPSb4]
                tensor.logical_z_list = []
                tensor.logical_x_list = []
            elif len(upper_neighbors) == 2:
                # Rule 3
                tensor.ups_list = [UPSc1, UPSc2, UPSc3, UPSc4, UPSc5, UPSc6]
                tensor.stabilizer_list = [UPSc1, UPSc2]
                tensor.logical_z_list = []
    return tensor_list
