from hqec.operator_push.hypertiling_compatibility.srg_to_htn import (
    create_directed_polygons,
    generate_poly_id_mapping,
    generate_tensors_for_all_polys,
    generate_tiling_with_layers,
    swap_legs_for_same_layer_neighbor,
    update_all_tensor_connections,
)
from hqec.operator_push.network_toolbox import assign_layers_to_tensors
from hqec.operator_push.tensor_toolbox import (
    Tensor,
    add_logical_legs,
    get_tensor_from_id,
    swap_tensor_legs,
    traverse_h_gate,
)


def setup_htn(l):
    # Define parameters
    p, q = 4, 5
    n = l + 2

    # Create a SRG object
    tiling_obj, layers_info = generate_tiling_with_layers(p=p, q=q, n=n)

    # Create directed polygons
    directed_polygons = create_directed_polygons(tiling_obj=tiling_obj, layers_info=layers_info)

    # Create poly id mapping to correct SRG id bug
    poly_id_mapping = generate_poly_id_mapping(tiling_obj, layers_info)

    # Create empty tensor list
    tensor_list = []

    # Create and connect tensors
    generate_tensors_for_all_polys(
        directed_polygons=directed_polygons, poly_id_mapping=poly_id_mapping, tensor_list=tensor_list
    )
    update_all_tensor_connections(tensor_list)

    # Assign layer to tensors
    assign_layers_to_tensors(tensor_list)

    # Correct leg order
    swap_legs_for_same_layer_neighbor(tensor_list)

    # Add logical legs
    add_logical_legs(tensor_list, 0, len(tensor_list))

    # Add H Gate
    traverse_h_gate(tensor_list)

    # Define UPS generators
    UPS1 = ["X", "X", "X", "X", "I"]
    UPS2 = ["Z", "I", "Z", "I", "I"]
    UPS3 = ["I", "Z", "I", "Z", "I"]
    UPS4 = ["I", "X", "I", "X", "X"]
    UPS5 = ["I", "I", "Z", "Z", "Z"]

    # Assign UPS to tensors
    for tensor in tensor_list:
        tensor.ups_list = [UPS1, UPS2, UPS3, UPS4, UPS5]

        # Rule application
        neighbor_layers = [get_tensor_from_id(tensor_list, tensor_id).layer for tensor_id in tensor.get_connections()]
        current_layer = tensor.layer

        if all(neighbor_layer > current_layer for neighbor_layer in neighbor_layers):
            # Rule 1
            tensor.stabilizer_list = [UPS1, UPS2, UPS3]
            tensor.logical_z_list = [UPS5]
            tensor.logical_x_list = [UPS4]
        elif any(neighbor_layer < current_layer for neighbor_layer in neighbor_layers):
            upper_neighbors = [layer for layer in neighbor_layers if layer < current_layer]
            same_layer_neighbors = [layer for layer in neighbor_layers if layer == current_layer]
            if len(upper_neighbors) == 1 and len(same_layer_neighbors) == 0:
                # Rule 2
                tensor.stabilizer_list = [UPS3]
                tensor.logical_z_list = [UPS5]
                tensor.logical_x_list = [UPS4]
            elif len(upper_neighbors) == 2 and len(same_layer_neighbors) == 0:
                # Rule 4
                tensor.stabilizer_list = []
                tensor.logical_z_list = [UPS3]
                # Swap legs 1 and 4
                swap_tensor_legs(tensor, 1, 4, tensor_list)
                tensor.incomplete_logical = True
            else:
                # Rule 3
                tensor.stabilizer_list = []
                tensor.logical_z_list = [UPS5]
                tensor.logical_x_list = [UPS4]

    return tensor_list


def setup_htn_z_fixed(l):
    # Define parameters
    p, q = 4, 5
    n = l + 2

    # Create a SRG object
    tiling_obj, layers_info = generate_tiling_with_layers(p=p, q=q, n=n)

    # Create directed polygons
    directed_polygons = create_directed_polygons(tiling_obj=tiling_obj, layers_info=layers_info)

    # Create poly id mapping to correct SRG id bug
    poly_id_mapping = generate_poly_id_mapping(tiling_obj, layers_info)

    # Create empty tensor list
    tensor_list = []

    if l == 0:
        tensor_0 = Tensor(tensor_id=0, num_legs=4)
        tensor_list.append(tensor_0)
        # Add logical legs
        add_logical_legs(tensor_list, 0, 1)
        # Define UPS generators
        UPS1 = ["X", "X", "X", "X", "I"]
        UPS2 = ["Z", "I", "Z", "I", "I"]
        UPS3 = ["I", "Z", "I", "Z", "I"]
        UPS4 = ["I", "X", "I", "X", "X"]
        UPS5 = ["I", "I", "Z", "Z", "Z"]
        tensor_0.ups_list = [UPS1, UPS2, UPS3, UPS4, UPS5]
        tensor_0.stabilizer_list = [UPS1, UPS2, UPS3]
        tensor_0.logical_z_list = [UPS5]
        tensor_0.logical_x_list = [UPS4]
        tensor_0.all_ups = [UPS1, UPS2, UPS3, UPS4, UPS5]
        return tensor_list

    # Create and connect tensors
    generate_tensors_for_all_polys(
        directed_polygons=directed_polygons, poly_id_mapping=poly_id_mapping, tensor_list=tensor_list
    )
    update_all_tensor_connections(tensor_list)

    # Assign layer to tensors
    assign_layers_to_tensors(tensor_list)

    # Correct leg order
    swap_legs_for_same_layer_neighbor(tensor_list)

    # Add logical legs
    add_logical_legs(tensor_list, 0, 1)

    # Add H Gate
    traverse_h_gate(tensor_list)

    # Define UPS generators
    UPS1 = ["X", "X", "X", "X", "I"]
    UPS2 = ["Z", "I", "Z", "I", "I"]
    UPS3 = ["I", "Z", "I", "Z", "I"]
    UPS4 = ["I", "X", "I", "X", "X"]
    UPS5 = ["I", "I", "Z", "Z", "Z"]

    # Define UPS generators
    UPSb1 = ["X", "X", "X", "X"]
    UPSb2 = ["Z", "I", "Z", "I"]
    UPSb3 = ["I", "Z", "I", "Z"]
    UPSb4 = ["I", "X", "I", "X"]
    UPSb5 = ["I", "I", "Z", "Z"]

    # Assign UPS to tensors
    for tensor in tensor_list:
        # tensor.ups_list = [UPS1, UPS2, UPS3, UPS4, UPS5]

        # Rule application
        neighbor_layers = [get_tensor_from_id(tensor_list, tensor_id).layer for tensor_id in tensor.get_connections()]
        current_layer = tensor.layer
        if all(neighbor_layer > current_layer for neighbor_layer in neighbor_layers):
            # Rule 1
            tensor.ups_list = [UPS1, UPS2, UPS3, UPS4, UPS5]
            tensor.stabilizer_list = [UPS1, UPS2, UPS3]
            tensor.logical_z_list = [UPS5]
            tensor.logical_x_list = [UPS4]
            tensor.all_ups = [UPS1, UPS2, UPS3, UPS4, UPS5]
        elif any(neighbor_layer < current_layer for neighbor_layer in neighbor_layers):
            upper_neighbors = [layer for layer in neighbor_layers if layer < current_layer]
            same_layer_neighbors = [layer for layer in neighbor_layers if layer == current_layer]
            if len(upper_neighbors) == 1 and len(same_layer_neighbors) == 0:
                # Rule 2
                tensor.ups_list = [UPSb1, UPSb2, UPSb3, UPSb5]
                tensor.stabilizer_list = [UPSb3, UPSb5]
                tensor.logical_z_list = []
                tensor.logical_x_list = []
                tensor.all_ups = [UPSb1, UPSb2, UPSb3, UPSb5]
            elif len(upper_neighbors) == 2 and len(same_layer_neighbors) == 0:
                # Rule 4
                tensor.ups_list = [UPSb1, UPSb2, UPSb3, UPSb4]
                tensor.stabilizer_list = []
                tensor.logical_z_list = []
                tensor.all_ups = [UPSb1, UPSb2, UPSb3, UPSb4]
                # Swap legs 1 and 4
                # swap_tensor_legs(tensor, 1, 4, tensor_list)
                # tensor.incomplete_logical = True
            else:
                # Rule 3
                tensor.ups_list = [UPSb1, UPSb2, UPSb3, UPSb5]
                tensor.stabilizer_list = [UPSb5]
                tensor.logical_z_list = []
                tensor.logical_x_list = []
                tensor.all_ups = [UPSb1, UPSb2, UPSb3, UPSb5]

    return tensor_list


def setup_htn_y_fixed(l):
    # Define parameters
    p, q = 4, 5
    n = l + 2

    # Create a SRG object
    tiling_obj, layers_info = generate_tiling_with_layers(p=p, q=q, n=n)

    # Create directed polygons
    directed_polygons = create_directed_polygons(tiling_obj=tiling_obj, layers_info=layers_info)

    # Create poly id mapping to correct SRG id bug
    poly_id_mapping = generate_poly_id_mapping(tiling_obj, layers_info)

    # Create empty tensor list
    tensor_list = []

    if l == 0:
        tensor_0 = Tensor(tensor_id=0, num_legs=4)
        tensor_list.append(tensor_0)
        # Add logical legs
        add_logical_legs(tensor_list, 0, 1)
        # Define UPS generators
        UPS1 = ["X", "X", "X", "X", "I"]
        UPS2 = ["Z", "I", "Z", "I", "I"]
        UPS3 = ["I", "Z", "I", "Z", "I"]
        UPS4 = ["I", "X", "I", "X", "X"]
        UPS5 = ["I", "I", "Z", "Z", "Z"]
        tensor_0.ups_list = [UPS1, UPS2, UPS3, UPS4, UPS5]
        tensor_0.stabilizer_list = [UPS1, UPS2, UPS3]
        tensor_0.logical_z_list = [UPS5]
        tensor_0.logical_x_list = [UPS4]
        tensor_0.all_ups = [UPS1, UPS2, UPS3, UPS4, UPS5]
        return tensor_list

    # Create and connect tensors
    generate_tensors_for_all_polys(
        directed_polygons=directed_polygons, poly_id_mapping=poly_id_mapping, tensor_list=tensor_list
    )
    update_all_tensor_connections(tensor_list)

    # Assign layer to tensors
    assign_layers_to_tensors(tensor_list)

    # Correct leg order
    swap_legs_for_same_layer_neighbor(tensor_list)

    # Add logical legs
    add_logical_legs(tensor_list, 0, 1)

    # Add H Gate
    traverse_h_gate(tensor_list)

    # Define UPS generators
    UPS1 = ["X", "X", "X", "X", "I"]
    UPS2 = ["Z", "I", "Z", "I", "I"]
    UPS3 = ["I", "Z", "I", "Z", "I"]
    UPS4 = ["I", "X", "I", "X", "X"]
    UPS5 = ["I", "I", "Z", "Z", "Z"]

    # Define UPS generators
    UPSb1 = ["X", "X", "X", "X"]
    UPSb2 = ["Z", "I", "Z", "I"]
    UPSb3 = ["I", "Z", "I", "Z"]
    UPSb4 = ["I", "X", "I", "X"]
    UPSb5 = ["I", "I", "Z", "Z"]
    UPSb6 = ["I", "X", "Z", "Y"]

    # Assign UPS to tensors
    for tensor in tensor_list:
        # tensor.ups_list = [UPS1, UPS2, UPS3, UPS4, UPS5]

        # Rule application
        neighbor_layers = [get_tensor_from_id(tensor_list, tensor_id).layer for tensor_id in tensor.get_connections()]
        current_layer = tensor.layer

        if all(neighbor_layer > current_layer for neighbor_layer in neighbor_layers):
            # Rule 1
            tensor.ups_list = [UPS1, UPS2, UPS3, UPS4, UPS5]
            tensor.stabilizer_list = [UPS1, UPS2, UPS3]
            tensor.logical_z_list = [UPS5]
            tensor.logical_x_list = [UPS4]
            tensor.all_ups = [UPS1, UPS2, UPS3, UPS4, UPS5]
        elif any(neighbor_layer < current_layer for neighbor_layer in neighbor_layers):
            upper_neighbors = [layer for layer in neighbor_layers if layer < current_layer]
            same_layer_neighbors = [layer for layer in neighbor_layers if layer == current_layer]
            if len(upper_neighbors) == 1 and len(same_layer_neighbors) == 0:
                # Rule 2
                tensor.ups_list = [UPSb1, UPSb2, UPSb3, UPSb6]
                tensor.stabilizer_list = [UPSb3, UPSb6]
                tensor.logical_z_list = []
                tensor.logical_x_list = []
                tensor.all_ups = [UPSb1, UPSb2, UPSb3, UPSb5]
            elif len(upper_neighbors) == 2 and len(same_layer_neighbors) == 0:
                # Rule 4
                tensor.ups_list = [UPSb1, UPSb2, UPSb3, UPSb4]
                tensor.stabilizer_list = []
                tensor.logical_z_list = []
                tensor.all_ups = [UPSb1, UPSb2, UPSb3, UPSb4]
                # Swap legs 1 and 4
                # swap_tensor_legs(tensor, 1, 4, tensor_list)
                # tensor.incomplete_logical = True
            else:
                # Rule 3
                tensor.ups_list = [UPSb1, UPSb2, UPSb3, UPSb6]
                tensor.stabilizer_list = [UPSb6]
                tensor.logical_z_list = []
                tensor.logical_x_list = []
                tensor.all_ups = [UPSb1, UPSb2, UPSb3, UPSb5]

    return tensor_list


# tl = setup_htn_z_fixed(l=1)
# for t in tl:
#     print(f"id:{t.tensor_id}, ups:{t.all_ups}")
