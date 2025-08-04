from LEGO_HQEC.OperatorPush.NetworkToolbox import create_layer_q4, assign_layers_to_tensors
from LEGO_HQEC.OperatorPush.TensorToolbox import ensure_minimum_legs, add_logical_legs, get_tensor_from_id, Tensor


def setup_steane_plus_rm_zero(R):
    if type(R) is not int:
        raise ValueError("R is not int")
    elif R < 0:
        raise ValueError("R < 0 is not allowed")
    tensor_list = []
    layer_list = []
    if R == 0:
        tensor_0 = Tensor(num_legs=0, tensor_id=0)
        tensor_list.append(tensor_0)
        # Ensure Minimum Legs to 7 for tensor0
        ensure_minimum_legs(tensor_list=tensor_list, target_leg_number=7, start_idx=0, end_idx=1)
    elif R == 1:
        r1 = create_layer_q4(tensor_list=tensor_list, previous_layer_id_list=[0], legs_per_tensor=7)
        layer_list.append(r1)
    else:
        r1 = create_layer_q4(tensor_list=tensor_list, previous_layer_id_list=[0], legs_per_tensor=7)
        layer_list.append(r1)
        for i, R_num in enumerate(range(2, R + 1)):
            if i % 2 == 0:
                temp = create_layer_q4(tensor_list=tensor_list, previous_layer_id_list=layer_list[i], legs_per_tensor=16)
            else:
                temp = create_layer_q4(tensor_list=tensor_list, previous_layer_id_list=layer_list[i], legs_per_tensor=8)
            layer_list.append(temp)

    for i, current_layer_tensor_id_list in enumerate(layer_list):
        if i % 2 == 0:
            # Ensure Minimum Legs to 16 for tensors in this layer
            ensure_minimum_legs(tensor_list=tensor_list, target_leg_number=16, start_idx=current_layer_tensor_id_list[0],
                                end_idx=current_layer_tensor_id_list[-1] + 1)
        else:
            # Ensure Minimum Legs to 6 for tensors in this layer
            ensure_minimum_legs(tensor_list=tensor_list, target_leg_number=8, start_idx=current_layer_tensor_id_list[0],
                                end_idx=current_layer_tensor_id_list[-1] + 1)

    # Add Logical
    add_logical_legs(tensor_list=tensor_list, start_idx=0, end_idx=1)

    # Assign layer
    assign_layers_to_tensors(tensor_list=tensor_list, center_tensor_id=0)

    # Define rm UPS generators
    upsa1 = "ZIZIZIZIZIZIZIZI"
    upsa2 = "IZZIIZZIIZZIIZZI"
    upsa3 = "IIIZZZZIIIIZZZZI"
    upsa4 = "IIIIIIIZZZZZZZZI"
    upsa5 = "IIZIIIZIIIZIIIZI"
    upsa6 = "IIIIZIZIIIIIZIZI"
    upsa7 = "IIIIIZZIIIIIIZZI"
    upsa8 = "IIIIIIIIIZZIIZZI"
    upsa9 = "IIIIIIIIIIIZZZZI"
    upsa10 = "IIIIIIIIZIZIZIZI"
    upsa11 = "XIXIXIXIXIXIXIXI"
    upsa12 = "IXXIIXXIIXXIIXXI"
    upsa13 = "IIIXXXXIIIIXXXXI"
    upsa14 = "IIIIIIIXXXXXXXXI"
    upsa15 = "XXXXXXXXXXXXXXXX"
    upsa16 = "ZZZZZZZZZZZZZZZZ"

    upsb1 = "IZIZIZIZIZIZIZIZ"
    upsb2 = "IIZZIIZZIIZZIIZZ"
    upsb3 = "IIIIZZZZIIIIZZZZ"
    upsb4 = "IIIIIIIIZZZZZZZZ"
    upsb5 = "IIIZIIIZIIIZIIIZ"
    upsb6 = "IIIIIZIZIIIIIZIZ"
    upsb7 = "IIIIIIZZIIIIIIZZ"
    upsb8 = "IIIIIIIIIIZZIIZZ"
    upsb9 = "IIIIIIIIIIIIZZZZ"
    upsb10 = "IIIIIIIIIZIZIZIZ"
    upsb11 = "IXIXIXIXIXIXIXIX"
    upsb12 = "IIXXIIXXIIXXIIXX"
    upsb13 = "IIIIXXXXIIIIXXXX"
    upsb14 = "IIIIIIIIXXXXXXXX"
    upsb15 = "XXXXXXXXXXXXXXXX"
    upsb16 = "ZZZZZZZZZZZZZZZZ"
    upsb17 = "YYYYYYYYYYYYYYYY"

    upsc1 = "ZIZIZIZIZIZIZIZI"
    upsc1y = "YIYIYIYIYIYIYIYI"
    upscyz = "YZXIYZXIYZXIYZXI"
    upscyx = "YXZIYXZIYXZIYXZI"
    upsc2 = "IZZIIZZIIZZIIZZI"
    upscxz = "XZYIXZYIXZYIXZYI"
    upscz = "ZZIIZZIIZZIIZZII"
    upsc2y = "IYYIIYYIIYYIIYYI"
    upsczy = "ZYXIZYXIZYXIZYXI"
    upscxy = "XYZIXYZIXYZIXYZI"
    upsc3y = "YYIIYYIIYYIIYYII"
    upsc3 = "IIIZZZZIIIIZZZZI"
    upsc4 = "IIIIIIIZZZZZZZZI"
    upsc5 = "IIZIIIZIIIZIIIZI"
    upsc6 = "IIIIZIZIIIIIZIZI"
    upsc7 = "IIIIIZZIIIIIIZZI"
    upsc8 = "IIIIIIIIIZZIIZZI"
    upsc9 = "IIIIIIIIIIIZZZZI"
    upsc10 = "IIIIIIIIZIZIZIZI"
    upsc11 = "XIXIXIXIXIXIXIXI"
    upscx = "XXIIXXIIXXIIXXII"
    upsc12 = "IXXIIXXIIXXIIXXI"
    upsczx = "ZXYIZXYIZXYIZXYI"
    upsc13 = "IIIXXXXIIIIXXXXI"
    upsc14 = "IIIIIIIXXXXXXXXI"
    upsc15 = "IIXXIIXXIIXXIIXX"
    upsc16 = "IIZZIIZZIIZZIIZZ"


    # Define happy UPS generators
    UPSa1 = ['X', 'X', 'X', 'I', 'I', 'I', 'X', 'I']
    UPSa2 = ['X', 'I', 'X', 'X', 'X', 'I', 'I', 'I']
    UPSa3 = ['X', 'I', 'I', 'I', 'X', 'X', 'X', 'I']
    UPSa4 = ['Z', 'Z', 'Z', 'I', 'I', 'I', 'Z', 'I']
    UPSa5 = ['Z', 'I', 'Z', 'Z', 'Z', 'I', 'I', 'I']
    UPSa6 = ['Z', 'I', 'I', 'I', 'Z', 'Z', 'Z', 'I']
    UPSa7 = ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X']
    UPSa8 = ['Z', 'Z', 'Z', 'Z', 'Z', 'Z', 'Z', 'Z']

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
                # Rule 2
                if current_layer % 2 == 1:
                    tensor.ups_list = [upsb1, upsb2, upsb3, upsb4, upsb5, upsb6, upsb7, upsb8, upsb9, upsb10, upsb11,
                                       upsb12, upsb13, upsb14, upsb15, upsb16, upsb17]
                    tensor.stabilizer_list = [upsb1, upsb2, upsb3, upsb4, upsb5, upsb6, upsb7, upsb8, upsb9, upsb10,
                                              upsb11, upsb12, upsb13, upsb14]
                else:
                    tensor.ups_list = [UPSc1, UPSc2, UPSc3, UPSc4, UPSc5, UPSc6, UPSc7, UPSc8]
                    tensor.stabilizer_list = [UPSc1, UPSc2, UPSc3, UPSc4, UPSc5, UPSc6]
                    tensor.logical_z_list = []
                    tensor.logical_x_list = []
            elif len(upper_neighbors) == 2:
                # Rule 3
                if current_layer % 2 == 1:
                    tensor.ups_list = [upsc1, upsc2, upsc3, upsc4, upsc5, upsc6, upsc7, upsc8, upsc9, upsc10, upsc11,
                                       upsc12, upsc13, upsc14, upsc15, upsc16, upsc1y, upsc2y, upsc3y, upscz, upscx,
                                       upscyz, upsczx, upscyx, upsczy, upscxy, upscxy, upscxz]
                    tensor.stabilizer_list = [upsc3, upsc4, upsc5, upsc6, upsc7, upsc8, upsc9, upsc10, upsc13, upsc14,
                                              upsc15, upsc16]
                else:
                    tensor.ups_list = [UPSd1, UPSd2, UPSd3, UPSd4, UPSd5, UPSd6, UPSd7, UPSd8]
                    tensor.stabilizer_list = [UPSd2, UPSd3, UPSd5, UPSd6]
    return tensor_list