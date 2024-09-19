from hqec.operator_push.network_toolbox import assign_layers_to_tensors, create_layer_q4
from hqec.operator_push.tensor_toolbox import Tensor, add_logical_legs, ensure_minimum_legs, get_tensor_from_id


def setup_happy_plus_rm_zero(R):
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
                temp = create_layer_q4(
                    tensor_list=tensor_list, previous_layer_id_list=layer_list[i], legs_per_tensor=16
                )
            else:
                temp = create_layer_q4(tensor_list=tensor_list, previous_layer_id_list=layer_list[i], legs_per_tensor=6)
            layer_list.append(temp)

    for i, current_layer_tensor_id_list in enumerate(layer_list):
        if i % 2 == 0:
            # Ensure Minimum Legs to 16 for tensors in this layer
            ensure_minimum_legs(
                tensor_list=tensor_list,
                target_leg_number=16,
                start_idx=current_layer_tensor_id_list[0],
                end_idx=current_layer_tensor_id_list[-1] + 1,
            )
        else:
            # Ensure Minimum Legs to 6 for tensors in this layer
            ensure_minimum_legs(
                tensor_list=tensor_list,
                target_leg_number=6,
                start_idx=current_layer_tensor_id_list[0],
                end_idx=current_layer_tensor_id_list[-1] + 1,
            )

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
    hUPSa1 = "XZZXII"
    hUPSa2 = "IXZZXI"
    hUPSa3 = "XIXZZI"
    hUPSa4 = "ZXIXZI"
    hUPSa5 = "XXXXXX"
    hUPSa6 = "ZZZZZZ"

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
            tensor.ups_list = [hUPSa1, hUPSa2, hUPSa3, hUPSa4, hUPSa5, hUPSa6]
            tensor.stabilizer_list = [hUPSa1, hUPSa2, hUPSa3, hUPSa4]
            tensor.logical_z_list = [hUPSa6]
            tensor.logical_x_list = [hUPSa5]
        elif any(neighbor_layer < current_layer for neighbor_layer in neighbor_layers):
            upper_neighbors = [layer for layer in neighbor_layers if layer < current_layer]
            if len(upper_neighbors) == 1:
                # Rule 2
                if current_layer % 2 == 1:
                    tensor.ups_list = [
                        upsb1,
                        upsb2,
                        upsb3,
                        upsb4,
                        upsb5,
                        upsb6,
                        upsb7,
                        upsb8,
                        upsb9,
                        upsb10,
                        upsb11,
                        upsb12,
                        upsb13,
                        upsb14,
                        upsb15,
                        upsb16,
                        upsb17,
                    ]
                    tensor.stabilizer_list = [
                        upsb1,
                        upsb2,
                        upsb3,
                        upsb4,
                        upsb5,
                        upsb6,
                        upsb7,
                        upsb8,
                        upsb9,
                        upsb10,
                        upsb11,
                        upsb12,
                        upsb13,
                        upsb14,
                    ]
                else:
                    tensor.ups_list = [UPSb1, UPSb2, UPSb3, UPSb4, UPSb5, UPSb6]
                    tensor.stabilizer_list = [UPSb1, UPSb2, UPSb3, UPSb4]
                    tensor.logical_z_list = []
                    tensor.logical_x_list = []
            elif len(upper_neighbors) == 2:
                # Rule 3
                if current_layer % 2 == 1:
                    tensor.ups_list = [
                        upsc1,
                        upsc2,
                        upsc3,
                        upsc4,
                        upsc5,
                        upsc6,
                        upsc7,
                        upsc8,
                        upsc9,
                        upsc10,
                        upsc11,
                        upsc12,
                        upsc13,
                        upsc14,
                        upsc15,
                        upsc16,
                        upsc1y,
                        upsc2y,
                        upsc3y,
                        upscz,
                        upscx,
                        upscyz,
                        upsczx,
                        upscyx,
                        upsczy,
                        upscxy,
                        upscxy,
                        upscxz,
                    ]
                    tensor.stabilizer_list = [
                        upsc3,
                        upsc4,
                        upsc5,
                        upsc6,
                        upsc7,
                        upsc8,
                        upsc9,
                        upsc10,
                        upsc13,
                        upsc14,
                        upsc15,
                        upsc16,
                    ]
                else:
                    tensor.ups_list = ul
                    tensor.stabilizer_list = [ul[0], ul[1]]
                    tensor.logical_z_list = []
    return tensor_list
