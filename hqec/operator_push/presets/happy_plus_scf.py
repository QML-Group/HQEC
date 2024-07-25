from hqec.operator_push.network_toolbox import create_layer_q4, assign_layers_to_tensors
from hqec.operator_push.tensor_toolbox import ensure_minimum_legs, add_logical_legs, get_tensor_from_id, Tensor


def setup_happy_plus_scf_max(R):
    if type(R) is not int:
        raise ValueError("R is not int")
    elif R < 0:
        raise ValueError("R < 0 is not allowed")
    tensor_list = []
    layer_list = []
    if R == 0:
        tensor_0 = Tensor(num_legs=0, tensor_id=0)
        tensor_list.append(tensor_0)
    elif R == 1:
        r1 = create_layer_q4(tensor_list=tensor_list, previous_layer_id_list=[0], legs_per_tensor=5)
        layer_list.append(r1)
    else:
        r1 = create_layer_q4(tensor_list=tensor_list, previous_layer_id_list=[0], legs_per_tensor=5)
        layer_list.append(r1)
        for i, R_num in enumerate(range(2, R + 1)):
            temp = create_layer_q4(tensor_list=tensor_list, previous_layer_id_list=layer_list[i], legs_per_tensor=5)
            layer_list.append(temp)

    # Ensure Minimum Legs to 5 for all tensors
    ensure_minimum_legs(tensor_list=tensor_list, target_leg_number=5, start_idx=0, end_idx=len(tensor_list))

    # Add Logical
    add_logical_legs(tensor_list=tensor_list, start_idx=0, end_idx=len(tensor_list))

    # Assign layer
    assign_layers_to_tensors(tensor_list=tensor_list, center_tensor_id=0)

    # Define SCF UPS generators
    sUPSa1 = 'IXXIXI'
    sUPSa2 = 'XIIXXI'
    sUPSa3 = 'IZIZZI'
    sUPSa4 = 'ZIZIZI'
    sUPSa5 = 'IXIXIX'
    sUPSa6 = 'ZIIZIZ'

    sUPSb1 = 'IXXIXI'
    sUPSb2 = 'XIIXXI'
    sUPSb3 = 'IZIZZI'
    sUPSb4 = 'ZIZIZI'
    sUPSb5 = 'IXIXIX'
    sUPSb6 = 'IIZZZZ'

    sUPSc1 = 'IXXIXI'
    sUPSc2 = 'XIIXXI'
    sUPSc3 = 'IZIZZI'
    sUPSc4 = 'ZIZIZI'
    sUPSc5 = 'IIXXXX'
    sUPSc6 = 'IIZZZZ'

    # Define happy UPS generators
    hUPSa1 = 'XZZXII'
    hUPSa2 = 'IXZZXI'
    hUPSa3 = 'XIXZZI'
    hUPSa4 = 'ZXIXZI'
    hUPSa5 = 'XXXXXX'
    hUPSa6 = 'ZZZZZZ'

    # Assign UPS to tensors
    for tensor in tensor_list:

        # Rule application
        neighbor_layers = [get_tensor_from_id(tensor_list, tensor_id).layer for tensor_id in tensor.get_connections()]
        current_layer = tensor.layer

        if all(neighbor_layer > current_layer for neighbor_layer in neighbor_layers):
            # Rule 1
            tensor.ups_list = [hUPSa1, hUPSa2, hUPSa3, hUPSa4, hUPSa5, hUPSa6]
            tensor.stabilizer_list = [hUPSa1, hUPSa2, hUPSa3, hUPSa4]
            tensor.logical_z_list = [hUPSa6]
            tensor.logical_x_list = [hUPSa5]
        elif any(neighbor_layer < current_layer for neighbor_layer in neighbor_layers):
            upper_neighbors = [layer for layer in neighbor_layers if layer < current_layer]
            if len(upper_neighbors) == 1:
                # Rule 2
                tensor.ups_list = [sUPSb1, sUPSb2, sUPSb3, sUPSb4, sUPSb5, sUPSb6]
                tensor.stabilizer_list = [sUPSb1, sUPSb3]
                tensor.logical_z_list = [sUPSb6]
                tensor.logical_x_list = [sUPSb5]
            elif len(upper_neighbors) == 2:
                # Rule 3
                tensor.ups_list = [sUPSc1, sUPSc2, sUPSc3, sUPSc4, sUPSc5, sUPSc6]
                tensor.stabilizer_list = []
                tensor.logical_z_list = [sUPSc6]
                tensor.logical_x_list = [sUPSc5]
    return tensor_list
