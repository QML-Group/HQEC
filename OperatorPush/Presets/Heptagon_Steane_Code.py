from OperatorPush.NetworkToolbox import create_layer_q4, assign_layers_to_tensors
from OperatorPush.TensorToolbox import ensure_minimum_legs, add_logical_legs, get_tensor_from_id, Tensor, has_logical


def setup_heptagon_max_rate_steane(R):
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
        r1 = create_layer_q4(tensor_list=tensor_list, previous_layer_id_list=[0], legs_per_tensor=7)
        layer_list.append(r1)
    else:
        r1 = create_layer_q4(tensor_list=tensor_list, previous_layer_id_list=[0], legs_per_tensor=7)
        layer_list.append(r1)
        for i, R_num in enumerate(range(2, R + 1)):
            temp = create_layer_q4(tensor_list=tensor_list, previous_layer_id_list=layer_list[i], legs_per_tensor=7)
            layer_list.append(temp)

    # Ensure Minimum Legs to 7 for all tensors
    ensure_minimum_legs(tensor_list=tensor_list, target_leg_number=7, start_idx=0, end_idx=len(tensor_list))

    # Add Logical
    add_logical_legs(tensor_list=tensor_list, start_idx=0, end_idx=len(tensor_list))

    # Assign layer
    assign_layers_to_tensors(tensor_list=tensor_list, center_tensor_id=0)

    # Define UPS generators
    UPSa1 = ['X', 'X', 'X', 'I', 'I', 'I', 'X', 'I']
    UPSa2 = ['X', 'I', 'X', 'X', 'X', 'I', 'I', 'I']
    UPSa3 = ['X', 'I', 'I', 'I', 'X', 'X', 'X', 'I']
    UPSa4 = ['Z', 'Z', 'Z', 'I', 'I', 'I', 'Z', 'I']
    UPSa5 = ['Z', 'I', 'Z', 'Z', 'Z', 'I', 'I', 'I']
    UPSa6 = ['Z', 'I', 'I', 'I', 'Z', 'Z', 'Z', 'I']
    UPSa7 = ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X']
    UPSa8 = ['Z', 'Z', 'Z', 'Z', 'Z', 'Z', 'Z', 'Z']

    UPSb1 = ['X', 'X', 'X', 'X', 'I', 'I', 'I', 'I']
    UPSb2 = ['I', 'X', 'I', 'X', 'X', 'X', 'I', 'I']
    UPSb3 = ['I', 'I', 'X', 'X', 'I', 'X', 'X', 'I']
    UPSb4 = ['Z', 'Z', 'Z', 'Z', 'I', 'I', 'I', 'I']
    UPSb5 = ['I', 'Z', 'I', 'Z', 'Z', 'Z', 'I', 'I']
    UPSb6 = ['I', 'I', 'Z', 'Z', 'I', 'Z', 'Z', 'I']
    UPSb7 = ['I', 'I', 'I', 'I', 'X', 'X', 'X', 'X']
    UPSb8 = ['I', 'I', 'I', 'I', 'Z', 'Z', 'Z', 'Z']

    ul = ['IIZZIZZI', 'IIXXIXXI', 'IZIZZZII', 'IXIXXXII', 'IYIYYYII', 'ZIIZZIZI', 'XIIXXIXI', 'YIIYYIYI', 'ZZIIIZZI', 'ZXIYYXZI', 'ZYIXXYZI', 'XZIYYZXI', 'YZIXXZYI', 'XXIIIXXI', 'XYIZZYXI', 'YXIZZXYI', 'YYIIIYYI']

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
        elif any(neighbor_layer < current_layer for neighbor_layer in neighbor_layers):
            upper_neighbors = [layer for layer in neighbor_layers if layer < current_layer]
            if len(upper_neighbors) == 1:
                # Rule 2
                tensor.ups_list = [UPSb1, UPSb2, UPSb3, UPSb4, UPSb5, UPSb6, UPSb7, UPSb8]
                tensor.stabilizer_list = [UPSb2, UPSb3, UPSb5, UPSb6]
                tensor.logical_z_list = [UPSb8]
                tensor.logical_x_list = [UPSb7]
            elif len(upper_neighbors) == 2:
                # Rule 3
                tensor.ups_list = ul
                tensor.stabilizer_list = [ul[0], ul[1]]
                tensor.logical_z_list = ['IIIIZZZZ']
                tensor.logical_x_list = ['IIIIXXXX']
    return tensor_list


def setup_heptagon_zero_rate_steane(R):
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
        r1 = create_layer_q4(tensor_list=tensor_list, previous_layer_id_list=[0], legs_per_tensor=7)
        layer_list.append(r1)
    else:
        r1 = create_layer_q4(tensor_list=tensor_list, previous_layer_id_list=[0], legs_per_tensor=7)
        layer_list.append(r1)
        for i, R_num in enumerate(range(2, R + 1)):
            temp = create_layer_q4(tensor_list=tensor_list, previous_layer_id_list=layer_list[i], legs_per_tensor=8)
            layer_list.append(temp)

    for i, current_layer_tensor_id_list in enumerate(layer_list):
        # Ensure Minimum Legs to 8 for tensors in this layer
        ensure_minimum_legs(tensor_list=tensor_list, target_leg_number=8, start_idx=current_layer_tensor_id_list[0],
                            end_idx=current_layer_tensor_id_list[-1] + 1)

    # Ensure Minimum Legs to 7 for tensor 0
    ensure_minimum_legs(tensor_list=tensor_list, target_leg_number=7, start_idx=0, end_idx=1)
    # Add Logical to tensor 0
    add_logical_legs(tensor_list=tensor_list, start_idx=0, end_idx=1)

    # Assign layer
    assign_layers_to_tensors(tensor_list=tensor_list, center_tensor_id=0)

    # Define UPS generators
    UPSa1 = ['X', 'X', 'X', 'I', 'I', 'I', 'X', 'I']
    UPSa2 = ['X', 'I', 'X', 'X', 'X', 'I', 'I', 'I']
    UPSa3 = ['X', 'I', 'I', 'I', 'X', 'X', 'X', 'I']
    UPSa4 = ['Z', 'Z', 'Z', 'I', 'I', 'I', 'Z', 'I']
    UPSa5 = ['Z', 'I', 'Z', 'Z', 'Z', 'I', 'I', 'I']
    UPSa6 = ['Z', 'I', 'I', 'I', 'Z', 'Z', 'Z', 'I']
    UPSa7 = ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X']
    UPSa8 = ['Z', 'Z', 'Z', 'Z', 'Z', 'Z', 'Z', 'Z']

    UPSb1 = ['X', 'X', 'X', 'X', 'I', 'I', 'I', 'I']
    UPSb2 = ['I', 'X', 'I', 'X', 'X', 'X', 'I', 'I']
    UPSb3 = ['I', 'I', 'X', 'X', 'I', 'X', 'X', 'I']
    UPSb4 = ['Z', 'Z', 'Z', 'Z', 'I', 'I', 'I', 'I']
    UPSb5 = ['I', 'Z', 'I', 'Z', 'Z', 'Z', 'I', 'I']
    UPSb6 = ['I', 'I', 'Z', 'Z', 'I', 'Z', 'Z', 'I']
    UPSb7 = ['I', 'I', 'I', 'I', 'X', 'X', 'X', 'X']
    UPSb8 = ['I', 'I', 'I', 'I', 'Z', 'Z', 'Z', 'Z']

    ul = ['IIZZIZZI', 'IIXXIXXI', 'IZIZZZII', 'IXIXXXII', 'IYIYYYII', 'ZIIZZIZI', 'XIIXXIXI', 'YIIYYIYI', 'ZZIIIZZI', 'ZXIYYXZI', 'ZYIXXYZI', 'XZIYYZXI', 'YZIXXZYI', 'XXIIIXXI', 'XYIZZYXI', 'YXIZZXYI', 'YYIIIYYI']

    UPSc1 = ['I', 'X', 'X', 'X', 'I', 'I', 'I', 'X']
    UPSc2 = ['I', 'X', 'I', 'X', 'X', 'X', 'I', 'I']
    UPSc3 = ['I', 'X', 'I', 'I', 'I', 'X', 'X', 'X']
    UPSc4 = ['I', 'Z', 'Z', 'Z', 'I', 'I', 'I', 'Z']
    UPSc5 = ['I', 'Z', 'I', 'Z', 'Z', 'Z', 'I', 'I']
    UPSc6 = ['I', 'Z', 'I', 'I', 'I', 'Z', 'Z', 'Z']
    UPSc7 = ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X']
    UPSc8 = ['Z', 'Z', 'Z', 'Z', 'Z', 'Z', 'Z', 'Z']

    UPSd1 = ['I', 'X', 'X', 'X', 'I', 'I', 'I', 'X']
    UPSd2 = ['I', 'I', 'I', 'X', 'X', 'X', 'I', 'X']
    UPSd3 = ['I', 'I', 'X', 'X', 'I', 'X', 'X', 'I']
    UPSd4 = ['I', 'Z', 'Z', 'Z', 'I', 'I', 'I', 'Z']
    UPSd5 = ['I', 'I', 'I', 'Z', 'Z', 'Z', 'I', 'Z']
    UPSd6 = ['I', 'I', 'Z', 'Z', 'I', 'Z', 'Z', 'I']
    UPSd7 = ['X', 'I', 'I', 'I', 'X', 'X', 'X', 'I']
    UPSd8 = ['Z', 'I', 'I', 'I', 'Z', 'Z', 'Z', 'I']

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
                if has_logical(tensor):
                    # Rule 2.b
                    tensor.ups_list = [UPSb1, UPSb2, UPSb3, UPSb4, UPSb5, UPSb6, UPSb7, UPSb8]
                    tensor.stabilizer_list = [UPSb2, UPSb3, UPSb5, UPSb6]
                    tensor.logical_z_list = [UPSb8]
                    tensor.logical_x_list = [UPSb7]
                    tensor.all_ups = [UPSb1, UPSb2, UPSb3, UPSb4, UPSb5, UPSb6, UPSb7, UPSb8]
                else:
                    # Rule 2.c
                    tensor.ups_list = [UPSc1, UPSc2, UPSc3, UPSc4, UPSc5, UPSc6, UPSc7, UPSc8]
                    tensor.stabilizer_list = [UPSc1, UPSc2, UPSc3, UPSc4, UPSc5, UPSc6]
                    tensor.all_ups = [UPSc1, UPSc2, UPSc3, UPSc4, UPSc5, UPSc6, UPSc7, UPSc8]
            elif len(upper_neighbors) == 2:
                if has_logical(tensor):
                    # Rule 3.1
                    tensor.ups_list = ul
                    tensor.stabilizer_list = [ul[0], ul[1]]
                    tensor.logical_z_list = ['IIIIZZZZ']
                    tensor.logical_x_list = ['IIIIXXXX']
                    tensor.all_ups = [ul[0], ul[1], ul[2], ul[3], ul[5], ul[6], 'IIIIZZZZ', 'IIIIXXXX']
                else:
                    # Rule 3.2
                    tensor.ups_list = [UPSd1, UPSd2, UPSd3, UPSd4, UPSd5, UPSd6, UPSd7, UPSd8]
                    tensor.stabilizer_list = [UPSd2, UPSd3, UPSd5, UPSd6]
                    tensor.all_ups = [UPSd1, UPSd2, UPSd3, UPSd4, UPSd5, UPSd6, UPSd7, UPSd8]
    return tensor_list


def setup_heptagon_const_rate_type_one_steane(R):
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
        r1 = create_layer_q4(tensor_list=tensor_list, previous_layer_id_list=[0], legs_per_tensor=7)
        layer_list.append(r1)
    else:
        r1 = create_layer_q4(tensor_list=tensor_list, previous_layer_id_list=[0], legs_per_tensor=7)
        layer_list.append(r1)
        for i, R_num in enumerate(range(2, R + 1)):
            if i % 2 == 0:
                temp = create_layer_q4(tensor_list=tensor_list, previous_layer_id_list=layer_list[i], legs_per_tensor=8)
                layer_list.append(temp)
            else:
                temp = create_layer_q4(tensor_list=tensor_list, previous_layer_id_list=layer_list[i], legs_per_tensor=7)
                layer_list.append(temp)

    for i, current_layer_tensor_id_list in enumerate(layer_list):
        if i % 2 == 0:
            # Ensure Minimum Legs to 8 for tensors in this layer
            ensure_minimum_legs(tensor_list=tensor_list, target_leg_number=8, start_idx=current_layer_tensor_id_list[0],
                                end_idx=current_layer_tensor_id_list[-1] + 1)
        else:
            # Ensure Minimum Legs to 7 for tensors in this layer
            ensure_minimum_legs(tensor_list=tensor_list, target_leg_number=7, start_idx=current_layer_tensor_id_list[0],
                                end_idx=current_layer_tensor_id_list[-1] + 1)
            # Add Logical
            add_logical_legs(tensor_list=tensor_list, start_idx=current_layer_tensor_id_list[0],
                             end_idx=current_layer_tensor_id_list[-1] + 1)

    # Ensure Minimum Legs to 7 for tensor 0
    ensure_minimum_legs(tensor_list=tensor_list, target_leg_number=7, start_idx=0, end_idx=1)
    # Add Logical to tensor 0
    add_logical_legs(tensor_list=tensor_list, start_idx=0, end_idx=1)

    # Assign layer
    assign_layers_to_tensors(tensor_list=tensor_list, center_tensor_id=0)

    # Define UPS generators
    UPSa1 = ['X', 'X', 'X', 'I', 'I', 'I', 'X', 'I']
    UPSa2 = ['X', 'I', 'X', 'X', 'X', 'I', 'I', 'I']
    UPSa3 = ['X', 'I', 'I', 'I', 'X', 'X', 'X', 'I']
    UPSa4 = ['Z', 'Z', 'Z', 'I', 'I', 'I', 'Z', 'I']
    UPSa5 = ['Z', 'I', 'Z', 'Z', 'Z', 'I', 'I', 'I']
    UPSa6 = ['Z', 'I', 'I', 'I', 'Z', 'Z', 'Z', 'I']
    UPSa7 = ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X']
    UPSa8 = ['Z', 'Z', 'Z', 'Z', 'Z', 'Z', 'Z', 'Z']

    UPSb1 = ['X', 'X', 'X', 'X', 'I', 'I', 'I', 'I']
    UPSb2 = ['I', 'X', 'I', 'X', 'X', 'X', 'I', 'I']
    UPSb3 = ['I', 'I', 'X', 'X', 'I', 'X', 'X', 'I']
    UPSb4 = ['Z', 'Z', 'Z', 'Z', 'I', 'I', 'I', 'I']
    UPSb5 = ['I', 'Z', 'I', 'Z', 'Z', 'Z', 'I', 'I']
    UPSb6 = ['I', 'I', 'Z', 'Z', 'I', 'Z', 'Z', 'I']
    UPSb7 = ['I', 'I', 'I', 'I', 'X', 'X', 'X', 'X']
    UPSb8 = ['I', 'I', 'I', 'I', 'Z', 'Z', 'Z', 'Z']

    ul = ['IIZZIZZI', 'IIXXIXXI', 'IZIZZZII', 'IXIXXXII', 'IYIYYYII', 'ZIIZZIZI', 'XIIXXIXI', 'YIIYYIYI', 'ZZIIIZZI', 'ZXIYYXZI', 'ZYIXXYZI', 'XZIYYZXI', 'YZIXXZYI', 'XXIIIXXI', 'XYIZZYXI', 'YXIZZXYI', 'YYIIIYYI']

    UPSc1 = ['I', 'X', 'X', 'X', 'I', 'I', 'I', 'X']
    UPSc2 = ['I', 'X', 'I', 'X', 'X', 'X', 'I', 'I']
    UPSc3 = ['I', 'X', 'I', 'I', 'I', 'X', 'X', 'X']
    UPSc4 = ['I', 'Z', 'Z', 'Z', 'I', 'I', 'I', 'Z']
    UPSc5 = ['I', 'Z', 'I', 'Z', 'Z', 'Z', 'I', 'I']
    UPSc6 = ['I', 'Z', 'I', 'I', 'I', 'Z', 'Z', 'Z']
    UPSc7 = ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X']
    UPSc8 = ['Z', 'Z', 'Z', 'Z', 'Z', 'Z', 'Z', 'Z']

    UPSd1 = ['I', 'X', 'X', 'X', 'I', 'I', 'I', 'X']
    UPSd2 = ['I', 'I', 'I', 'X', 'X', 'X', 'I', 'X']
    UPSd3 = ['I', 'I', 'X', 'X', 'I', 'X', 'X', 'I']
    UPSd4 = ['I', 'Z', 'Z', 'Z', 'I', 'I', 'I', 'Z']
    UPSd5 = ['I', 'I', 'I', 'Z', 'Z', 'Z', 'I', 'Z']
    UPSd6 = ['I', 'I', 'Z', 'Z', 'I', 'Z', 'Z', 'I']
    UPSd7 = ['X', 'I', 'I', 'I', 'X', 'X', 'X', 'I']
    UPSd8 = ['Z', 'I', 'I', 'I', 'Z', 'Z', 'Z', 'I']

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
        elif any(neighbor_layer < current_layer for neighbor_layer in neighbor_layers):
            upper_neighbors = [layer for layer in neighbor_layers if layer < current_layer]
            if len(upper_neighbors) == 1:
                if has_logical(tensor):
                    # Rule 2.b
                    tensor.ups_list = [UPSb1, UPSb2, UPSb3, UPSb4, UPSb5, UPSb6, UPSb7, UPSb8]
                    tensor.stabilizer_list = [UPSb2, UPSb3, UPSb5, UPSb6]
                    tensor.logical_z_list = [UPSb8]
                    tensor.logical_x_list = [UPSb7]
                else:
                    # Rule 2.c
                    tensor.ups_list = [UPSc1, UPSc2, UPSc3, UPSc4, UPSc5, UPSc6, UPSc7, UPSc8]
                    tensor.stabilizer_list = [UPSc1, UPSc2, UPSc3, UPSc4, UPSc5, UPSc6]
            elif len(upper_neighbors) == 2:
                if has_logical(tensor):
                    # Rule 3.1
                    tensor.ups_list = ul
                    tensor.stabilizer_list = [ul[0], ul[1]]
                    tensor.logical_z_list = ['IIIIZZZZ']
                    tensor.logical_x_list = ['IIIIXXXX']
                else:
                    # Rule 3.2
                    tensor.ups_list = [UPSd1, UPSd2, UPSd3, UPSd4, UPSd5, UPSd6, UPSd7, UPSd8]
                    tensor.stabilizer_list = [UPSd2, UPSd3, UPSd5, UPSd6]
    return tensor_list


def setup_heptagon_const_rate_type_two_steane(R):
    if type(R) is not int:
        raise ValueError("R is not int")
    elif R < 0:
        raise ValueError("R < 0 is not allowed")
    tensor_list = []
    layer_list = []
    if R == 0:
        r1 = create_layer_q4(tensor_list=tensor_list, previous_layer_id_list=[0], legs_per_tensor=7)
        layer_list.append(r1)
    else:
        r1 = create_layer_q4(tensor_list=tensor_list, previous_layer_id_list=[0], legs_per_tensor=7)
        layer_list.append(r1)
        for i, R_num in enumerate(range(2, R + 1)):
            temp = create_layer_q4(tensor_list=tensor_list, previous_layer_id_list=layer_list[i], legs_per_tensor=7)
            layer_list.append(temp)
        temp = create_layer_q4(tensor_list=tensor_list, previous_layer_id_list=layer_list[-1], legs_per_tensor=7)
        layer_list.append(temp)

    for current_layer_tensor_id_list in layer_list[:-1]:
        # Ensure Minimum Legs to 7 for tensors in this layer
        ensure_minimum_legs(tensor_list=tensor_list, target_leg_number=7, start_idx=current_layer_tensor_id_list[0],
                            end_idx=current_layer_tensor_id_list[-1] + 1)
        # Add Logical
        add_logical_legs(tensor_list=tensor_list, start_idx=current_layer_tensor_id_list[0],
                         end_idx=current_layer_tensor_id_list[-1] + 1)

    last_layer_tensor_id_list = layer_list[-1]
    # Ensure Minimum Legs to 8 for tensors in this layer
    ensure_minimum_legs(tensor_list=tensor_list, target_leg_number=8, start_idx=last_layer_tensor_id_list[0],
                        end_idx=last_layer_tensor_id_list[-1] + 1)

    # Ensure Minimum Legs to 7 for tensor 0
    ensure_minimum_legs(tensor_list=tensor_list, target_leg_number=7, start_idx=0, end_idx=1)
    # Add Logical to tensor 0
    add_logical_legs(tensor_list=tensor_list, start_idx=0, end_idx=1)

    # Assign layer
    assign_layers_to_tensors(tensor_list=tensor_list, center_tensor_id=0)

    # Define UPS generators
    UPSa1 = ['X', 'X', 'X', 'I', 'I', 'I', 'X', 'I']
    UPSa2 = ['X', 'I', 'X', 'X', 'X', 'I', 'I', 'I']
    UPSa3 = ['X', 'I', 'I', 'I', 'X', 'X', 'X', 'I']
    UPSa4 = ['Z', 'Z', 'Z', 'I', 'I', 'I', 'Z', 'I']
    UPSa5 = ['Z', 'I', 'Z', 'Z', 'Z', 'I', 'I', 'I']
    UPSa6 = ['Z', 'I', 'I', 'I', 'Z', 'Z', 'Z', 'I']
    UPSa7 = ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X']
    UPSa8 = ['Z', 'Z', 'Z', 'Z', 'Z', 'Z', 'Z', 'Z']

    UPSb1 = ['X', 'X', 'X', 'X', 'I', 'I', 'I', 'I']
    UPSb2 = ['I', 'X', 'I', 'X', 'X', 'X', 'I', 'I']
    UPSb3 = ['I', 'I', 'X', 'X', 'I', 'X', 'X', 'I']
    UPSb4 = ['Z', 'Z', 'Z', 'Z', 'I', 'I', 'I', 'I']
    UPSb5 = ['I', 'Z', 'I', 'Z', 'Z', 'Z', 'I', 'I']
    UPSb6 = ['I', 'I', 'Z', 'Z', 'I', 'Z', 'Z', 'I']
    UPSb7 = ['I', 'I', 'I', 'I', 'X', 'X', 'X', 'X']
    UPSb8 = ['I', 'I', 'I', 'I', 'Z', 'Z', 'Z', 'Z']

    ul = ['IIZZIZZI', 'IIXXIXXI', 'IZIZZZII', 'IXIXXXII', 'IYIYYYII', 'ZIIZZIZI', 'XIIXXIXI', 'YIIYYIYI', 'ZZIIIZZI', 'ZXIYYXZI', 'ZYIXXYZI', 'XZIYYZXI', 'YZIXXZYI', 'XXIIIXXI', 'XYIZZYXI', 'YXIZZXYI', 'YYIIIYYI']

    UPSc1 = ['I', 'X', 'X', 'X', 'I', 'I', 'I', 'X']
    UPSc2 = ['I', 'X', 'I', 'X', 'X', 'X', 'I', 'I']
    UPSc3 = ['I', 'X', 'I', 'I', 'I', 'X', 'X', 'X']
    UPSc4 = ['I', 'Z', 'Z', 'Z', 'I', 'I', 'I', 'Z']
    UPSc5 = ['I', 'Z', 'I', 'Z', 'Z', 'Z', 'I', 'I']
    UPSc6 = ['I', 'Z', 'I', 'I', 'I', 'Z', 'Z', 'Z']
    UPSc7 = ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X']
    UPSc8 = ['Z', 'Z', 'Z', 'Z', 'Z', 'Z', 'Z', 'Z']

    UPSd1 = ['I', 'X', 'X', 'X', 'I', 'I', 'I', 'X']
    UPSd2 = ['I', 'I', 'I', 'X', 'X', 'X', 'I', 'X']
    UPSd3 = ['I', 'I', 'X', 'X', 'I', 'X', 'X', 'I']
    UPSd4 = ['I', 'Z', 'Z', 'Z', 'I', 'I', 'I', 'Z']
    UPSd5 = ['I', 'I', 'I', 'Z', 'Z', 'Z', 'I', 'Z']
    UPSd6 = ['I', 'I', 'Z', 'Z', 'I', 'Z', 'Z', 'I']
    UPSd7 = ['X', 'I', 'I', 'I', 'X', 'X', 'X', 'I']
    UPSd8 = ['Z', 'I', 'I', 'I', 'Z', 'Z', 'Z', 'I']

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
        elif any(neighbor_layer < current_layer for neighbor_layer in neighbor_layers):
            upper_neighbors = [layer for layer in neighbor_layers if layer < current_layer]
            if len(upper_neighbors) == 1:
                if has_logical(tensor):
                    # Rule 2.b
                    tensor.ups_list = [UPSb1, UPSb2, UPSb3, UPSb4, UPSb5, UPSb6, UPSb7, UPSb8]
                    tensor.stabilizer_list = [UPSb2, UPSb3, UPSb5, UPSb6]
                    tensor.logical_z_list = [UPSb8]
                    tensor.logical_x_list = [UPSb7]
                else:
                    # Rule 2.c
                    tensor.ups_list = [UPSc1, UPSc2, UPSc3, UPSc4, UPSc5, UPSc6, UPSc7, UPSc8]
                    tensor.stabilizer_list = [UPSc1, UPSc2, UPSc3, UPSc4, UPSc5, UPSc6]
            elif len(upper_neighbors) == 2:
                if has_logical(tensor):
                    # Rule 3.1
                    tensor.ups_list = ul
                    tensor.stabilizer_list = [ul[0], ul[1]]
                    tensor.logical_z_list = ['IIIIZZZZ']
                    tensor.logical_x_list = ['IIIIXXXX']
                else:
                    # Rule 3.2
                    tensor.ups_list = [UPSd1, UPSd2, UPSd3, UPSd4, UPSd5, UPSd6, UPSd7, UPSd8]
                    tensor.stabilizer_list = [UPSd2, UPSd3, UPSd5, UPSd6]
    return tensor_list


def setup_heptagon_const_rate_type_three_steane(R):
    if type(R) is not int:
        raise ValueError("R is not int")
    elif R < 0:
        raise ValueError("R < 0 is not allowed")
    tensor_list = []
    layer_list = []
    if R == 0:
        r1 = create_layer_q4(tensor_list=tensor_list, previous_layer_id_list=[0], legs_per_tensor=7)
        layer_list.append(r1)
        temp = create_layer_q4(tensor_list=tensor_list, previous_layer_id_list=layer_list[0], legs_per_tensor=7)
        layer_list.append(temp)
    else:
        r1 = create_layer_q4(tensor_list=tensor_list, previous_layer_id_list=[0], legs_per_tensor=7)
        layer_list.append(r1)
        for i, R_num in enumerate(range(2, R + 1)):
            temp = create_layer_q4(tensor_list=tensor_list, previous_layer_id_list=layer_list[i], legs_per_tensor=7)
            layer_list.append(temp)
        temp = create_layer_q4(tensor_list=tensor_list, previous_layer_id_list=layer_list[-1], legs_per_tensor=7)
        layer_list.append(temp)
        temp = create_layer_q4(tensor_list=tensor_list, previous_layer_id_list=layer_list[-1], legs_per_tensor=7)
        layer_list.append(temp)

    for current_layer_tensor_id_list in layer_list[:-2]:
        # Ensure Minimum Legs to 7 for tensors in this layer
        ensure_minimum_legs(tensor_list=tensor_list, target_leg_number=7, start_idx=current_layer_tensor_id_list[0],
                            end_idx=current_layer_tensor_id_list[-1] + 1)
        # Add Logical
        add_logical_legs(tensor_list=tensor_list, start_idx=current_layer_tensor_id_list[0],
                         end_idx=current_layer_tensor_id_list[-1] + 1)

    sec_last_layer_tensor_id_list = layer_list[-2]
    last_layer_tensor_id_list = layer_list[-1]
    # Ensure Minimum Legs to 8 for tensors in this layer
    ensure_minimum_legs(tensor_list=tensor_list, target_leg_number=8, start_idx=sec_last_layer_tensor_id_list[0],
                        end_idx=sec_last_layer_tensor_id_list[-1] + 1)
    ensure_minimum_legs(tensor_list=tensor_list, target_leg_number=8, start_idx=last_layer_tensor_id_list[0],
                        end_idx=last_layer_tensor_id_list[-1] + 1)

    # Ensure Minimum Legs to 7 for tensor 0
    ensure_minimum_legs(tensor_list=tensor_list, target_leg_number=7, start_idx=0, end_idx=1)
    # Add Logical to tensor 0
    add_logical_legs(tensor_list=tensor_list, start_idx=0, end_idx=1)

    # Assign layer
    assign_layers_to_tensors(tensor_list=tensor_list, center_tensor_id=0)

    # Define UPS generators
    UPSa1 = ['X', 'X', 'X', 'I', 'I', 'I', 'X', 'I']
    UPSa2 = ['X', 'I', 'X', 'X', 'X', 'I', 'I', 'I']
    UPSa3 = ['X', 'I', 'I', 'I', 'X', 'X', 'X', 'I']
    UPSa4 = ['Z', 'Z', 'Z', 'I', 'I', 'I', 'Z', 'I']
    UPSa5 = ['Z', 'I', 'Z', 'Z', 'Z', 'I', 'I', 'I']
    UPSa6 = ['Z', 'I', 'I', 'I', 'Z', 'Z', 'Z', 'I']
    UPSa7 = ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X']
    UPSa8 = ['Z', 'Z', 'Z', 'Z', 'Z', 'Z', 'Z', 'Z']

    UPSb1 = ['X', 'X', 'X', 'X', 'I', 'I', 'I', 'I']
    UPSb2 = ['I', 'X', 'I', 'X', 'X', 'X', 'I', 'I']
    UPSb3 = ['I', 'I', 'X', 'X', 'I', 'X', 'X', 'I']
    UPSb4 = ['Z', 'Z', 'Z', 'Z', 'I', 'I', 'I', 'I']
    UPSb5 = ['I', 'Z', 'I', 'Z', 'Z', 'Z', 'I', 'I']
    UPSb6 = ['I', 'I', 'Z', 'Z', 'I', 'Z', 'Z', 'I']
    UPSb7 = ['I', 'I', 'I', 'I', 'X', 'X', 'X', 'X']
    UPSb8 = ['I', 'I', 'I', 'I', 'Z', 'Z', 'Z', 'Z']

    ul = ['IIZZIZZI', 'IIXXIXXI', 'IZIZZZII', 'IXIXXXII', 'IYIYYYII', 'ZIIZZIZI', 'XIIXXIXI', 'YIIYYIYI', 'ZZIIIZZI', 'ZXIYYXZI', 'ZYIXXYZI', 'XZIYYZXI', 'YZIXXZYI', 'XXIIIXXI', 'XYIZZYXI', 'YXIZZXYI', 'YYIIIYYI']

    UPSc1 = ['I', 'X', 'X', 'X', 'I', 'I', 'I', 'X']
    UPSc2 = ['I', 'X', 'I', 'X', 'X', 'X', 'I', 'I']
    UPSc3 = ['I', 'X', 'I', 'I', 'I', 'X', 'X', 'X']
    UPSc4 = ['I', 'Z', 'Z', 'Z', 'I', 'I', 'I', 'Z']
    UPSc5 = ['I', 'Z', 'I', 'Z', 'Z', 'Z', 'I', 'I']
    UPSc6 = ['I', 'Z', 'I', 'I', 'I', 'Z', 'Z', 'Z']
    UPSc7 = ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X']
    UPSc8 = ['Z', 'Z', 'Z', 'Z', 'Z', 'Z', 'Z', 'Z']

    UPSd1 = ['I', 'X', 'X', 'X', 'I', 'I', 'I', 'X']
    UPSd2 = ['I', 'I', 'I', 'X', 'X', 'X', 'I', 'X']
    UPSd3 = ['I', 'I', 'X', 'X', 'I', 'X', 'X', 'I']
    UPSd4 = ['I', 'Z', 'Z', 'Z', 'I', 'I', 'I', 'Z']
    UPSd5 = ['I', 'I', 'I', 'Z', 'Z', 'Z', 'I', 'Z']
    UPSd6 = ['I', 'I', 'Z', 'Z', 'I', 'Z', 'Z', 'I']
    UPSd7 = ['X', 'I', 'I', 'I', 'X', 'X', 'X', 'I']
    UPSd8 = ['Z', 'I', 'I', 'I', 'Z', 'Z', 'Z', 'I']

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
        elif any(neighbor_layer < current_layer for neighbor_layer in neighbor_layers):
            upper_neighbors = [layer for layer in neighbor_layers if layer < current_layer]
            if len(upper_neighbors) == 1:
                if has_logical(tensor):
                    # Rule 2.b
                    tensor.ups_list = [UPSb1, UPSb2, UPSb3, UPSb4, UPSb5, UPSb6, UPSb7, UPSb8]
                    tensor.stabilizer_list = [UPSb2, UPSb3, UPSb5, UPSb6]
                    tensor.logical_z_list = [UPSb8]
                    tensor.logical_x_list = [UPSb7]
                else:
                    # Rule 2.c
                    tensor.ups_list = [UPSc1, UPSc2, UPSc3, UPSc4, UPSc5, UPSc6, UPSc7, UPSc8]
                    tensor.stabilizer_list = [UPSc1, UPSc2, UPSc3, UPSc4, UPSc5, UPSc6]
            elif len(upper_neighbors) == 2:
                if has_logical(tensor):
                    # Rule 3.1
                    tensor.ups_list = ul
                    tensor.stabilizer_list = [ul[0], ul[1]]
                    tensor.logical_z_list = ['IIIIZZZZ']
                    tensor.logical_x_list = ['IIIIXXXX']
                else:
                    # Rule 3.2
                    tensor.ups_list = [UPSd1, UPSd2, UPSd3, UPSd4, UPSd5, UPSd6, UPSd7, UPSd8]
                    tensor.stabilizer_list = [UPSd2, UPSd3, UPSd5, UPSd6]
    return tensor_list
