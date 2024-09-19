from OperatorPush.NetworkToolbox import create_layer_q4, assign_layers_to_tensors
from OperatorPush.TensorToolbox import ensure_minimum_legs, add_logical_legs, get_tensor_from_id, Tensor


def setup_zero_rate_713(R):
    if type(R) is not int:
        raise ValueError("R is not int")
    elif R < 0:
        raise ValueError("R <= 0 is not allowed")
    tensor_list = []
    layer_list = []
    if R == 0:
        tensor_0 = Tensor(num_legs=0, tensor_id=0)
        tensor_list.append(tensor_0)
    elif R == 1:
        r1 = create_layer_q4(tensor_list, [0], 7)
        layer_list.append(r1)
    else:
        r1 = create_layer_q4(tensor_list, [0], 7)
        layer_list.append(r1)
        for i, R_num in enumerate(range(2, R + 1)):
            temp = create_layer_q4(tensor_list, layer_list[i], 8)
            layer_list.append(temp)

    # Ensure Minimum Legs to 7 for tensor 0
    ensure_minimum_legs(tensor_list, 7, 0, 1)

    # Ensure Minimum Legs to 8 for other tensors
    ensure_minimum_legs(tensor_list, 8, 1, len(tensor_list))

    # Add Logical
    add_logical_legs(tensor_list, 0, 1)

    # Assign layer
    assign_layers_to_tensors(tensor_list, 0)

    # Define UPS generators
    UPSa1 = 'XZIZXIII'
    UPSa2 = 'IXZIZXII'
    UPSa3 = 'IIXZIZXI'
    UPSa4 = 'XIIXZIZI'
    UPSa5 = 'ZXIIXZII'
    UPSa6 = 'IZXIIXZI'
    UPSa7 = 'XXXXXXXX'
    UPSa8 = 'ZZZZZZZZ'

    UPSb1 = 'IXZIZXII'
    UPSb2 = 'IIXZIZXI'
    UPSb3 = 'IIIXZIZX'
    UPSb4 = 'IXIIXZIZ'
    UPSb5 = 'IZXIIXZI'
    UPSb6 = 'IIZXIIXZ'
    UPSb7 = 'XXXXXXXX'
    UPSb8 = 'ZZZZZZZZ'

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
            tensor.ups_list = [UPSa1, UPSa2, UPSa3, UPSa4, UPSa5, UPSa6, UPSa7, UPSa8]
            tensor.stabilizer_list = [UPSa1, UPSa2, UPSa3, UPSa4, UPSa5, UPSa6]
            tensor.logical_z_list = [UPSa8]
            tensor.logical_x_list = [UPSa7]
            tensor.all_ups = [UPSa1, UPSa2, UPSa3, UPSa4, UPSa5, UPSa6, UPSa7, UPSa8]
        elif any(neighbor_layer < current_layer for neighbor_layer in neighbor_layers):
            upper_neighbors = [layer for layer in neighbor_layers if layer < current_layer]
            if len(upper_neighbors) == 1:
                # Rule 2
                tensor.ups_list = [UPSb1, UPSb2, UPSb3, UPSb4, UPSb5, UPSb6, UPSb7, UPSb8]
                tensor.stabilizer_list = [UPSb1, UPSb2, UPSb3, UPSb4, UPSb5, UPSb6]
                tensor.logical_z_list = []
                tensor.logical_x_list = []
                tensor.all_ups = [UPSb1, UPSb2, UPSb3, UPSb4, UPSb5, UPSb6, UPSb7, UPSb8]
            elif len(upper_neighbors) == 2:
                # Rule 3
                tensor.ups_list = [UPSc1, UPSc2, UPSc3, UPSc4, UPSc5, UPSc6]
                tensor.stabilizer_list = [UPSc1, UPSc2]
                tensor.logical_z_list = []
    return tensor_list
