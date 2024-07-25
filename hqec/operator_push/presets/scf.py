from hqec.operator_push.network_toolbox import create_layer_q4, assign_layers_to_tensors
from hqec.operator_push.tensor_toolbox import ensure_minimum_legs, add_logical_legs, get_tensor_from_id, Tensor, has_logical


def setup_max_rate_scf(R):
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

    # Define UPS generators
    UPSa1 = 'IXXIXI'
    UPSa2 = 'XIIXXI'
    UPSa3 = 'IZIZZI'
    UPSa4 = 'ZIZIZI'
    UPSa5 = 'IXIXIX'
    UPSa6 = 'ZIIZIZ'

    UPSb1 = 'IXXIXI'
    UPSb2 = 'XIIXXI'
    UPSb3 = 'IZIZZI'
    UPSb4 = 'ZIZIZI'
    UPSb5 = 'IXIXIX'
    UPSb6 = 'IIZZZZ'

    UPSc1 = 'IXXIXI'
    UPSc2 = 'XIIXXI'
    UPSc3 = 'IZIZZI'
    UPSc4 = 'ZIZIZI'
    UPSc5 = 'IIXXXX'
    UPSc6 = 'IIZZZZ'

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
                tensor.stabilizer_list = [UPSb1, UPSb3]
                tensor.logical_z_list = [UPSb6]
                tensor.logical_x_list = [UPSb5]
            elif len(upper_neighbors) == 2:
                # Rule 3
                tensor.ups_list = [UPSc1, UPSc2, UPSc3, UPSc4, UPSc5, UPSc6]
                tensor.stabilizer_list = []
                tensor.logical_z_list = [UPSc6]
                tensor.logical_x_list = [UPSc5]
    return tensor_list


def setup_zero_rate_scf(R):
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
            temp = create_layer_q4(tensor_list=tensor_list, previous_layer_id_list=layer_list[i], legs_per_tensor=6)
            layer_list.append(temp)

    for i, current_layer_tensor_id_list in enumerate(layer_list):
        # Ensure Minimum Legs to 6 for tensors in this layer
        ensure_minimum_legs(tensor_list=tensor_list, target_leg_number=6, start_idx=current_layer_tensor_id_list[0],
                            end_idx=current_layer_tensor_id_list[-1] + 1)

    # Ensure Minimum Legs to 5 for tensor 0
    ensure_minimum_legs(tensor_list=tensor_list, target_leg_number=5, start_idx=0, end_idx=1)
    # Add Logical to tensor 0
    add_logical_legs(tensor_list=tensor_list, start_idx=0, end_idx=1)

    # Assign layer
    assign_layers_to_tensors(tensor_list=tensor_list, center_tensor_id=0)

    # Define UPS generators
    UPSa1 = 'IXXIXI'
    UPSa2 = 'XIIXXI'
    UPSa3 = 'IZIZZI'
    UPSa4 = 'ZIZIZI'
    UPSa5 = 'IXIXIX'
    UPSa6 = 'ZIIZIZ'

    UPSb1 = 'IXXIXI'
    UPSb2 = 'XIIXXI'
    UPSb3 = 'IZIZZI'
    UPSb4 = 'ZIZIZI'
    UPSb5 = 'IXIXIX'
    UPSb6 = 'IIZZZZ'

    UPSc1 = 'IXXIXI'
    UPSc2 = 'XIIXXI'
    UPSc3 = 'IZIZZI'
    UPSc4 = 'ZIZIZI'
    UPSc5 = 'IIXXXX'
    UPSc6 = 'IIZZZZ'

    UPSd1 = 'IIXXIX'
    UPSd2 = 'IXIIXX'
    UPSd3 = 'IIZIZZ'
    UPSd4 = 'IZIZIZ'
    UPSd5 = 'XIXIXI'
    UPSd6 = 'ZIIZZZ'

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
            tensor.all_ups = [UPSa1, UPSa2, UPSa3, UPSa4, UPSa5, UPSa6]
        elif any(neighbor_layer < current_layer for neighbor_layer in neighbor_layers):
            upper_neighbors = [layer for layer in neighbor_layers if layer < current_layer]
            if len(upper_neighbors) == 1:
                if has_logical(tensor):
                    # Rule 2.1
                    tensor.ups_list = [UPSb1, UPSb2, UPSb3, UPSb4, UPSb5, UPSb6]
                    tensor.stabilizer_list = [UPSb1, UPSb3]
                    tensor.logical_z_list = [UPSb6]
                    tensor.logical_x_list = [UPSb5]
                    tensor.all_ups = [UPSb1, UPSb2, UPSb3, UPSb4, UPSb5, UPSb6]
                else:
                    # Rule 2.2
                    tensor.ups_list = [UPSd1, UPSd2, UPSd3, UPSd4, UPSd5, UPSd6]
                    tensor.stabilizer_list = [UPSd1, UPSd2, UPSd3, UPSd4]
                    tensor.all_ups = [UPSd1, UPSd2, UPSd3, UPSd4, UPSd5, UPSd6]
            elif len(upper_neighbors) == 2:
                if has_logical(tensor):
                    # Rule 3.1
                    tensor.ups_list = [UPSc1, UPSc2, UPSc3, UPSc4, UPSc5, UPSc6]
                    tensor.stabilizer_list = []
                    tensor.logical_z_list = [UPSc6]
                    tensor.logical_x_list = [UPSc5]
                    tensor.all_ups = [UPSc1, UPSc2, UPSc3, UPSc4, UPSc5, UPSc6]
                else:
                    # Rule 3.2
                    tensor.ups_list = [UPSd1, UPSd2, UPSd3, UPSd4, UPSd5, UPSd6]
                    tensor.stabilizer_list = [UPSd1, UPSd3]
                    tensor.all_ups = [UPSd1, UPSd2, UPSd3, UPSd4, UPSd5, UPSd6]
    return tensor_list
