from hqec.operator_push.network_toolbox import assign_layers_to_tensors, create_layer_q4
from hqec.operator_push.tensor_toolbox import Tensor, add_logical_legs, ensure_minimum_legs, get_tensor_from_id


def setup_happy_plus_steane_max(R):
    if type(R) is not int:
        raise ValueError("R is not int")
    elif R < 0:
        raise ValueError("R < 0 is not allowed")
    tensor_list = []
    layer_list = []
    if R == 0:
        tensor_0 = Tensor(num_legs=0, tensor_id=0)
        tensor_list.append(tensor_0)
        # Ensure Minimum Legs to 5 for tensor0
        ensure_minimum_legs(tensor_list=tensor_list, target_leg_number=5, start_idx=0, end_idx=1)
    elif R == 1:
        r1 = create_layer_q4(tensor_list=tensor_list, previous_layer_id_list=[0], legs_per_tensor=5)
        layer_list.append(r1)
    else:
        r1 = create_layer_q4(tensor_list=tensor_list, previous_layer_id_list=[0], legs_per_tensor=5)
        layer_list.append(r1)
        for i, R_num in enumerate(range(2, R + 1)):
            if i % 2 == 0:
                temp = create_layer_q4(tensor_list=tensor_list, previous_layer_id_list=layer_list[i], legs_per_tensor=7)
            else:
                temp = create_layer_q4(tensor_list=tensor_list, previous_layer_id_list=layer_list[i], legs_per_tensor=5)
            layer_list.append(temp)

    for i, current_layer_tensor_id_list in enumerate(layer_list):
        if i % 2 == 0:
            # Ensure Minimum Legs to 7 for tensors in this layer
            ensure_minimum_legs(
                tensor_list=tensor_list,
                target_leg_number=7,
                start_idx=current_layer_tensor_id_list[0],
                end_idx=current_layer_tensor_id_list[-1] + 1,
            )
        else:
            # Ensure Minimum Legs to 5 for tensors in this layer
            ensure_minimum_legs(
                tensor_list=tensor_list,
                target_leg_number=5,
                start_idx=current_layer_tensor_id_list[0],
                end_idx=current_layer_tensor_id_list[-1] + 1,
            )

    # Add Logical
    add_logical_legs(tensor_list=tensor_list, start_idx=0, end_idx=len(tensor_list))

    # Assign layer
    assign_layers_to_tensors(tensor_list=tensor_list, center_tensor_id=0)

    # Define Steane UPS generators
    UPSa1 = ["X", "X", "X", "I", "I", "I", "X", "I"]
    UPSa2 = ["X", "I", "X", "X", "X", "I", "I", "I"]
    UPSa3 = ["X", "I", "I", "I", "X", "X", "X", "I"]
    UPSa4 = ["Z", "Z", "Z", "I", "I", "I", "Z", "I"]
    UPSa5 = ["Z", "I", "Z", "Z", "Z", "I", "I", "I"]
    UPSa6 = ["Z", "I", "I", "I", "Z", "Z", "Z", "I"]
    UPSa7 = ["X", "X", "X", "X", "X", "X", "X", "X"]
    UPSa8 = ["Z", "Z", "Z", "Z", "Z", "Z", "Z", "Z"]

    UPSb1 = ["X", "X", "X", "X", "I", "I", "I", "I"]
    UPSb2 = ["I", "X", "I", "X", "X", "X", "I", "I"]
    UPSb3 = ["I", "I", "X", "X", "I", "X", "X", "I"]
    UPSb4 = ["Z", "Z", "Z", "Z", "I", "I", "I", "I"]
    UPSb5 = ["I", "Z", "I", "Z", "Z", "Z", "I", "I"]
    UPSb6 = ["I", "I", "Z", "Z", "I", "Z", "Z", "I"]
    UPSb7 = ["I", "I", "I", "I", "X", "X", "X", "X"]
    UPSb8 = ["I", "I", "I", "I", "Z", "Z", "Z", "Z"]

    ul = [
        "IIZZIZZI",
        "IIXXIXXI",
        "IZIZZZII",
        "IXIXXXII",
        "IYIYYYII",
        "ZIIZZIZI",
        "XIIXXIXI",
        "YIIYYIYI",
        "ZZIIIZZI",
        "ZXIYYXZI",
        "ZYIXXYZI",
        "XZIYYZXI",
        "YZIXXZYI",
        "XXIIIXXI",
        "XYIZZYXI",
        "YXIZZXYI",
        "YYIIIYYI",
    ]

    # Define happy UPS generators
    hUPSa1 = "XZZXII"
    hUPSa2 = "IXZZXI"
    hUPSa3 = "XIXZZI"
    hUPSa4 = "ZXIXZI"
    hUPSa5 = "XXXXXX"
    hUPSa6 = "ZZZZZZ"

    hulb = ["IXZZXI", "IZYYZI", "ZXXIZI", "XIZXZI", "YXYXII", "IZXIXZ", "IZZXIX", "IIYXXY"]

    hul = ["IZYYZI", "IXZZXI", "IYXXYI", "ZIZYYI", "XIXZZI", "YIYXXI", "IIYZYZ", "IIZXZX", "IIXYXY"]

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
                if current_layer % 2 == 1:
                    tensor.ups_list = [UPSb1, UPSb2, UPSb3, UPSb4, UPSb5, UPSb6, UPSb7, UPSb8]
                    tensor.stabilizer_list = [UPSb2, UPSb3, UPSb5, UPSb6]
                    tensor.logical_z_list = [UPSb8]
                    tensor.logical_x_list = [UPSb7]
                else:
                    tensor.ups_list = hulb
                    tensor.stabilizer_list = [hulb[0], hulb[1]]
                    tensor.logical_z_list = [hulb[5]]
                    tensor.logical_x_list = [hulb[6]]
            elif len(upper_neighbors) == 2:
                # Rule 3
                if current_layer % 2 == 1:
                    tensor.ups_list = ul
                    tensor.stabilizer_list = [ul[0], ul[1]]
                    tensor.logical_z_list = ["IIIIZZZZ"]
                    tensor.logical_x_list = ["IIIIXXXX"]
                else:
                    tensor.ups_list = hul
                    tensor.stabilizer_list = []
                    tensor.logical_z_list = [hul[6]]
                    tensor.logical_x_list = [hul[7]]
    return tensor_list
