from hqec.operator_push.network_toolbox import assign_layers_to_tensors, create_layer_q4
from hqec.operator_push.tensor_toolbox import Tensor, add_logical_legs, ensure_minimum_legs, get_tensor_from_id


def setup_zero_rate_happy(R):
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
    UPSa1 = ["X", "Z", "Z", "X", "I", "I"]
    UPSa2 = ["I", "X", "Z", "Z", "X", "I"]
    UPSa3 = ["X", "I", "X", "Z", "Z", "I"]
    UPSa4 = ["Z", "X", "I", "X", "Z", "I"]
    UPSa5 = ["X", "X", "X", "X", "X", "X"]
    UPSa6 = ["Z", "Z", "Z", "Z", "Z", "Z"]

    UPSb1 = ["I", "X", "Z", "Z", "X", "I"]
    UPSb2 = ["I", "I", "X", "Z", "Z", "X"]
    UPSb3 = ["I", "X", "I", "X", "Z", "Z"]
    UPSb4 = ["I", "Z", "X", "I", "X", "Z"]
    UPSb5 = ["X", "X", "X", "X", "X", "X"]
    UPSb6 = ["Z", "Z", "Z", "Z", "Z", "Z"]

    ul = [
        "IIXZZX",
        "IIZYYZ",
        "IZXXIZ",
        "IXIZXZ",
        "IYXYXI",
        "ZIZXIX",
        "XIZZXI",
        "YIIYXX",
        "ZZYIIY",
        "ZXZYXY",
        "ZYYZXX",
        "XZYYXZ",
        "YZXZXY",
        "XXZIIZ",
        "XYYXII",
        "YXIXIY",
        "YYXIIX",
    ]

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
                # Rule 2
                tensor.ups_list = [UPSb1, UPSb2, UPSb3, UPSb4, UPSb5, UPSb6]
                tensor.stabilizer_list = [UPSb1, UPSb2, UPSb3, UPSb4]
                tensor.logical_z_list = []
                tensor.logical_x_list = []
                tensor.all_ups = [UPSb1, UPSb2, UPSb3, UPSb4, UPSb5, UPSb6]
            elif len(upper_neighbors) == 2:
                # Rule 3
                tensor.ups_list = ul
                tensor.stabilizer_list = [ul[0], ul[1]]
                tensor.logical_z_list = []
                tensor.all_ups = [ul[0], ul[1], ul[2], ul[3], ul[5], ul[6]]
    return tensor_list


def setup_max_rate_happy(R):
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
        r1 = create_layer_q4(tensor_list, [0], 5)
        layer_list.append(r1)
    else:
        r1 = create_layer_q4(tensor_list, [0], 5)
        layer_list.append(r1)
        for i, R_num in enumerate(range(2, R + 1)):
            temp = create_layer_q4(tensor_list, layer_list[i], 5)
            layer_list.append(temp)

    # Ensure Minimum Legs to 5 for tensors
    ensure_minimum_legs(tensor_list, 5, 0, len(tensor_list))

    # Add Logical
    add_logical_legs(tensor_list, 0, len(tensor_list))

    # Assign layer
    assign_layers_to_tensors(tensor_list, 0)

    # Define UPS generators
    UPSa1 = ["X", "Z", "Z", "X", "I", "I"]
    UPSa2 = ["I", "X", "Z", "Z", "X", "I"]
    UPSa3 = ["X", "I", "X", "Z", "Z", "I"]
    UPSa4 = ["Z", "X", "I", "X", "Z", "I"]
    UPSa5 = ["X", "X", "X", "X", "X", "X"]
    UPSa6 = ["Z", "Z", "Z", "Z", "Z", "Z"]

    ulb = ["IXZZXI", "IZYYZI", "ZXXIZI", "XIZXZI", "YXYXII", "IZXIXZ", "IZZXIX", "IIYXXY"]

    ul = ["IZYYZI", "IXZZXI", "IYXXYI", "ZIZYYI", "XIXZZI", "YIYXXI", "IIYZYZ", "IIZXZX", "IIXYXY"]

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
                tensor.ups_list = ulb
                tensor.stabilizer_list = [ulb[0], ulb[1]]
                tensor.logical_z_list = [ulb[5]]
                tensor.logical_x_list = [ulb[6]]
            elif len(upper_neighbors) == 2:
                # Rule 3
                tensor.ups_list = ul
                tensor.stabilizer_list = []
                tensor.logical_z_list = [ul[6]]
                tensor.logical_x_list = [ul[7]]
    return tensor_list
