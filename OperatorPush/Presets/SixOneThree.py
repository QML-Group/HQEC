from OperatorPush.NetworkToolbox import create_layer_q4, assign_layers_to_tensors
from OperatorPush.TensorToolbox import ensure_minimum_legs, add_logical_legs, get_tensor_from_id, Tensor, has_logical

def setup_zero_rate_613(R):
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
        r1 = create_layer_q4(tensor_list=tensor_list, previous_layer_id_list=[0], legs_per_tensor=6)
        layer_list.append(r1)
    else:
        r1 = create_layer_q4(tensor_list=tensor_list, previous_layer_id_list=[0], legs_per_tensor=6)
        layer_list.append(r1)
        for i, R_num in enumerate(range(2, R + 1)):
            temp = create_layer_q4(tensor_list=tensor_list, previous_layer_id_list=layer_list[i], legs_per_tensor=7)
            layer_list.append(temp)

    for i, current_layer_tensor_id_list in enumerate(layer_list):
        # Ensure Minimum Legs to 7 for tensors in this layer
        ensure_minimum_legs(tensor_list=tensor_list, target_leg_number=7, start_idx=current_layer_tensor_id_list[0],
                            end_idx=current_layer_tensor_id_list[-1] + 1)

    # Ensure Minimum Legs to 5 for tensor 0
    ensure_minimum_legs(tensor_list=tensor_list, target_leg_number=6, start_idx=0, end_idx=1)
    # Add Logical to tensor 0
    add_logical_legs(tensor_list=tensor_list, start_idx=0, end_idx=1)

    # Assign layer
    assign_layers_to_tensors(tensor_list=tensor_list, center_tensor_id=0)

    # Define UPS generators
    UPSa1 = 'ZIZIIII'
    UPSa2 = 'XZYYXII'
    UPSa3 = 'XXXXZII'
    UPSa4 = 'IZZXIXI'
    UPSa5 = 'XYXYIZI'
    UPSa6 = 'XZXZIIX'
    UPSa7 = 'XYYXIIZ'

    UPSb1 = 'IZIZIII'
    UPSb2 = 'IXZYYXI'
    UPSb3 = 'IXXXXZI'
    UPSb4 = 'IIZZXIX'
    UPSb5 = 'IXYXYIZ'
    UPSb6 = 'XXZXZII'
    UPSb7 = 'ZXYYXII'
    UPSby = 'YIXZYII'

    UPSc1 = 'IIZIZII'
    UPSc2 = 'IIXZYYX'
    UPSc3 = 'IIXXXXZ'
    UPSc4 = 'XIIZZXI'
    UPSc5 = 'ZIXYXYI'
    UPSc6 = 'IXXZXZI'
    UPSc7 = 'IZXYYXI'
    UPSczz = 'ZZIIZZI'
    UPScxx = 'XXXIYYI'
    UPScyi = 'YIXXYZI'
    UPSciy = 'IYIXZYI'
    UPScyy = 'YYXIXXI'
    UPScyx = 'YXIYZII'
    UPScyz = 'YZIZIYI'
    UPScxy = 'XYIYIZI'
    UPSczy = 'ZYXZYII'



    # Assign UPS to tensors
    for tensor in tensor_list:

        # Rule application
        neighbor_layers = [get_tensor_from_id(tensor_list, tensor_id).layer for tensor_id in tensor.get_connections()]
        current_layer = tensor.layer

        if all(neighbor_layer > current_layer for neighbor_layer in neighbor_layers):
            # Rule 1
            tensor.ups_list = [UPSa1, UPSa2, UPSa3, UPSa4, UPSa5, UPSa6, UPSa7]
            tensor.stabilizer_list = [UPSa1, UPSa2, UPSa3, UPSa4, UPSa5]
            tensor.logical_z_list = [UPSa7]
            tensor.logical_x_list = [UPSa6]
            tensor.all_ups = [UPSa1, UPSa2, UPSa3, UPSa4, UPSa5, UPSa6, UPSa7]
        elif any(neighbor_layer < current_layer for neighbor_layer in neighbor_layers):
            upper_neighbors = [layer for layer in neighbor_layers if layer < current_layer]
            if len(upper_neighbors) == 1:
                # Rule 2.2
                tensor.ups_list = [UPSb1, UPSb2, UPSb3, UPSb4, UPSb5, UPSb6, UPSb7, UPSby]
                tensor.stabilizer_list = [UPSb1, UPSb2, UPSb3, UPSb4, UPSb5]
                tensor.all_ups = [UPSb1, UPSb2, UPSb3, UPSb4, UPSb5, UPSb6, UPSb7]
            if len(upper_neighbors) == 2:
                tensor.ups_list = [UPSc1, UPSc2, UPSc3, UPSc4, UPSc5, UPSc6, UPSc7, UPSczz, UPScxx, UPScyi, UPSciy,
                                   UPScyy, UPScyx, UPScyz, UPScxy, UPSczy]
                tensor.stabilizer_list = [UPSc1, UPSc2, UPSc3]
                tensor.all_ups = [UPSc1, UPSc2, UPSc3, UPSc4, UPSc5, UPSc6, UPSc7]
    return tensor_list
