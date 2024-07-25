from hqec.operator_push.tensor_toolbox import TensorLeg, Tensor, get_tensor_from_id, swap_tensor_legs
from hypertiling import HyperbolicTiling


def generate_tiling_with_layers(p, q, n):
    # Create a tiling object with only the central cell
    tiling_obj = HyperbolicTiling(p=p, q=q, n=1, kernel="SRG", center="cell")

    # Record the layer for each polygon
    layers_info = {0: 0}  # The central cell is always in layer 0

    # Repeat adding layers n-1 times to obtain a tiling_obj with n layers
    for layer in range(1, n):
        prev_count = len(tiling_obj)  # Number of polygons in the previous layer
        tiling_obj.add_layer()  # Add a new layer
        new_count = len(tiling_obj)  # Number of polygons in the new layer

        # Calculate the number of polygons in this layer and record the layer information
        for poly_id in range(prev_count, new_count):
            layers_info[poly_id] = layer

    return tiling_obj, layers_info


# Example usage:
# p, q, n are defined
# tiling_obj, layers_info = generate_tiling_with_layers(p, q, n)
# Now tiling_obj is the HyperbolicTiling object with n layers, and layers_info contains the layer number for each
# polygon id.


def share_common_edge(poly_id1, poly_id2, tiling_obj, q):
    # Get the neighbor lists for two polygons
    nbrs1 = set(tiling_obj.get_nbrs(poly_id1))
    nbrs2 = set(tiling_obj.get_nbrs(poly_id2))

    # Calculate the number of common neighbors
    common_nbrs = nbrs1.intersection(nbrs2)

    # If the number of common neighbors is equal to 2 * (q - 2), they share an edge
    return len(common_nbrs) == 2 * (q - 2)

# Example usage:
# Assuming T is an instance of HyperbolicTiling and q is defined
# result = share_common_edge(4, 6, T, q)
# print(result)  # Outputs True or False, depending on whether the polygons share an edge


def get_shared_edge_neighbors(poly_id, tiling_obj, q):
    # Get the IDs of all polygons that share a vertex with the specified polygon
    potential_neighbors = tiling_obj.get_nbrs(poly_id)

    # Initialize a list to store the IDs of neighbors sharing an edge
    shared_edge_neighbors = []

    # Check if each potential neighbor actually shares an edge
    for nbr_id in potential_neighbors:
        if share_common_edge(poly_id, nbr_id, tiling_obj, q):
            shared_edge_neighbors.append(nbr_id)

    return shared_edge_neighbors

# Example usage:
# Assuming T is an instance of HyperbolicTiling and q is defined
# shared_neighbors = get_shared_edge_neighbors(some_poly_id, T, q)
# print(shared_neighbors)  # This will print the list of IDs of all polygons sharing an edge with the specified polygon


class DirectedPolygon:
    def __init__(self, poly_id):
        self.poly_id = poly_id
        self.back = None
        self.left = None
        self.right = None
        self.front = None
        self.left_front = None
        self.right_front = None
        self.all_front = []

    def __str__(self):
        neighbors_info = f"Polygon ID: {self.poly_id}\n"
        neighbors_info += f"Back Neighbor: {self.back}\n"
        neighbors_info += f"Left Neighbor: {self.left}\n"
        neighbors_info += f"Right Neighbor: {self.right}\n"
        neighbors_info += f"Front Neighbor: {self.front}\n"
        neighbors_info += f"Left-Front Neighbor: {self.left_front}\n"
        neighbors_info += f"Right-Front Neighbor: {self.right_front}\n"
        neighbors_info += f"All-Front Neighbors: {self.all_front}\n"
        return neighbors_info


def determine_directed_neighbors(poly_id, tiling_obj, layers_info, q=5):
    # Create a DirectedPolygon instance
    directed_poly = DirectedPolygon(poly_id)

    # Get neighbors sharing an edge
    shared_edge_neighbors = get_shared_edge_neighbors(poly_id=poly_id, q=q, tiling_obj=tiling_obj)

    # Determine the IDs of polygons in the current layer
    current_layer_poly_ids = [id for id, layer in layers_info.items() if layer == layers_info[poly_id]]

    # Determine the IDs of polygons in the next layer
    next_layer_poly_ids = [id for id, layer in layers_info.items() if layer > layers_info[poly_id]]

    # Categorize neighbors
    same_layer_neighbors = [nbr for nbr in shared_edge_neighbors if layers_info[nbr] == layers_info[poly_id]]
    upper_layer_neighbors = [nbr for nbr in shared_edge_neighbors if layers_info[nbr] < layers_info[poly_id]]
    lower_layer_neighbors = [nbr for nbr in shared_edge_neighbors if layers_info[nbr] > layers_info[poly_id]]

    # Create a poly ID mapping
    poly_id_mapping = generate_poly_id_mapping(tiling_obj=tiling_obj, layers_info=layers_info)

    # Determine back and front neighbors
    if upper_layer_neighbors:
        directed_poly.back = upper_layer_neighbors[0]  # Assuming there's only one upper layer neighbor
    if lower_layer_neighbors:
        if len(lower_layer_neighbors) == 1:
            directed_poly.front = lower_layer_neighbors[0]
        else:
            directed_poly.all_front = lower_layer_neighbors

    # Use the poly ID mapping to ensure direction correctness, addressing a hypertiling bug
    same_layer_neighbors_mapped_poly_id = [poly_id_mapping[nbr] for nbr in same_layer_neighbors]

    # Determine left and right neighbors
    if same_layer_neighbors:
        # If the current polygon ID is not the smallest and largest in the layer
        if poly_id != min(current_layer_poly_ids) and poly_id != max(current_layer_poly_ids):
            directed_poly.left = find_key_by_value(dictionary=poly_id_mapping,
                                                   value=min(same_layer_neighbors_mapped_poly_id))
            directed_poly.right = find_key_by_value(dictionary=poly_id_mapping,
                                                    value=max(same_layer_neighbors_mapped_poly_id))
        else:
            directed_poly.left = find_key_by_value(dictionary=poly_id_mapping,
                                                   value=max(same_layer_neighbors_mapped_poly_id))
            directed_poly.right = find_key_by_value(dictionary=poly_id_mapping,
                                                    value=min(same_layer_neighbors_mapped_poly_id))

    # Use the poly ID mapping to ensure direction correctness, addressing a hypertiling bug
    lower_layer_neighbors_mapped_poly_id = [poly_id_mapping[nbr] for nbr in lower_layer_neighbors]

    # Determine left_front and right_front neighbors
    if len(lower_layer_neighbors) == 2:
        if min(lower_layer_neighbors) != min(next_layer_poly_ids) and \
                max(lower_layer_neighbors) != max(next_layer_poly_ids):
            directed_poly.left_front = find_key_by_value(dictionary=poly_id_mapping,
                                                         value=min(lower_layer_neighbors_mapped_poly_id))
            directed_poly.right_front = find_key_by_value(dictionary=poly_id_mapping,
                                                          value=max(lower_layer_neighbors_mapped_poly_id))
        else:
            directed_poly.left_front = find_key_by_value(dictionary=poly_id_mapping,
                                                         value=max(lower_layer_neighbors_mapped_poly_id))
            directed_poly.right_front = find_key_by_value(dictionary=poly_id_mapping,
                                                          value=min(lower_layer_neighbors_mapped_poly_id))

    return directed_poly


def create_directed_polygons(tiling_obj, layers_info):
    directed_polygons = {}

    # Create a DirectedPolygon object for each polygon ID in tiling_obj
    for poly_id in range(len(tiling_obj)):
        directed_polygon = determine_directed_neighbors(poly_id, tiling_obj, layers_info)
        directed_polygons[poly_id] = directed_polygon

    return directed_polygons

# Example usage:
# Assuming tiling_obj and layers_info are defined
# all_directed_polygons = create_directed_polygons(tiling_obj, layers_info)


def generate_poly_id_mapping(tiling_obj, layers_info):
    poly_id_mapping = {}
    for layer in sorted(set(layers_info.values())):
        if layer == 0:
            poly_id_mapping[0] = 0
            continue
        elif layer == max(sorted(set(layers_info.values()))):
            break
        # Find all polygon IDs in the current layer
        poly_ids_in_layer = [poly_id for poly_id, poly_layer in layers_info.items() if poly_layer == layer]
        # Sort by Hypertiling ID
        sorted_poly_ids = sorted(poly_ids_in_layer)

        # Set the mapping for the minimum ID to ensure we start correctly
        poly_id_mapping[sorted_poly_ids[0]] = sorted_poly_ids[0]
        next_expected_id = sorted_poly_ids[0] + 1

        # Iterate over the remaining IDs and create mappings
        shared_edge_neighbors = get_shared_edge_neighbors(sorted_poly_ids[0], tiling_obj, 5)
        same_layer_neighbors = [nbr for nbr in shared_edge_neighbors if layers_info[nbr] == layer]
        next_ht_id = min(same_layer_neighbors)
        previous_ht_id = sorted_poly_ids[0]
        while True:
            ht_id = next_ht_id
            shared_edge_neighbors = get_shared_edge_neighbors(ht_id, tiling_obj, 5)
            same_layer_neighbors = [nbr for nbr in shared_edge_neighbors if layers_info[nbr] == layer]
            # Create the mapping
            poly_id_mapping[ht_id] = next_expected_id
            same_layer_neighbors.remove(previous_ht_id)
            next_ht_id = list(same_layer_neighbors)[0]
            previous_ht_id = ht_id
            next_expected_id += 1
            if next_ht_id == sorted_poly_ids[0]:
                break

    return poly_id_mapping


def find_key_by_value(dictionary, value):
    for key, val in dictionary.items():
        if val == value:
            return key
    return None  # Return None if no matching key is found


def has_only_left_right_neighbors(poly_id, directed_polygons):
    # Retrieve the DirectedPolygon instance
    directed_poly = directed_polygons.get(poly_id)

    # Check if it has left and right neighbors and no back neighbor
    if directed_poly:
        has_left = directed_poly.left is not None
        has_right = directed_poly.right is not None
        has_back = directed_poly.back is not None

        return has_left and has_right and not has_back
    else:
        # If no DirectedPolygon instance is found, return False or raise an exception
        return False
        # Alternatively, you can raise an exception with a message
        # raise ValueError(f"No DirectedPolygon found with poly_id: {poly_id}")

# Example usage:
# directed_polygons = { ... } # Assuming this is a dictionary containing DirectedPolygon instances
# result = has_only_left_right_neighbors(12, directed_polygons)
# print(f"Poly ID 12 has only left and right neighbors: {result}")


def has_only_all_front_neighbors(poly_id, directed_polygons):
    # Retrieve the DirectedPolygon instance
    directed_poly = directed_polygons.get(poly_id)

    # Check if the polygon has only all_front neighbors
    if directed_poly:
        has_back = directed_poly.back is not None
        has_left = directed_poly.left is not None
        has_right = directed_poly.right is not None
        has_front = directed_poly.front is not None
        has_left_front = directed_poly.left_front is not None
        has_right_front = directed_poly.right_front is not None
        has_all_front = directed_poly.all_front is not None and directed_poly.all_front != []

        return has_all_front and not (has_back or has_left or has_right or has_front or has_left_front or has_right_front)
    else:
        # If no DirectedPolygon instance is found, return False or raise an exception
        return False
        # Alternatively, you can raise an exception with a message
        # raise ValueError(f"No DirectedPolygon found with poly_id: {poly_id}")

# Example usage:
# directed_polygons = { ... } # Assuming this is a dictionary containing DirectedPolygon instances
# result = has_only_all_front_neighbors(0, directed_polygons)
# print(f"Poly ID 0 has only all front neighbors: {result}")


def has_any_neighbor(poly_id, directed_polygons):
    # Retrieve the DirectedPolygon instance
    directed_poly = directed_polygons.get(poly_id)

    # Check if the polygon has neighbors in any direction
    if directed_poly:
        has_neighbors = any([
            directed_poly.back is not None,
            directed_poly.left is not None,
            directed_poly.right is not None,
            directed_poly.front is not None,
            directed_poly.left_front is not None,
            directed_poly.right_front is not None,
            directed_poly.all_front is not None and directed_poly.all_front != []
        ])
        return has_neighbors
    else:
        # If no DirectedPolygon instance is found, return False or raise an exception
        return False
        # Alternatively, you can raise an exception with a message
        # raise ValueError(f"No DirectedPolygon found with poly_id: {poly_id}")

# Example usage:
# directed_polygons = { ... } # Assuming this is a dictionary containing DirectedPolygon instances
# result = has_any_neighbor(0, directed_polygons)
# print(f"Poly ID 0 has any neighbor: {result}")


def generate_tensor_with_legs(poly_id, directed_polygons, poly_id_mapping, tensor_list):
    # Check if the current polygon has any neighbors
    if not has_any_neighbor(poly_id, directed_polygons):
        return  # Don't create a tensor if there are no neighbors

    # Get the DirectedPolygon object for the current polygon
    directed_poly = directed_polygons[poly_id]

    # Create a tensor
    tensor_id = poly_id_mapping[poly_id]
    tensor = Tensor(tensor_id, 0)

    # Determine the order and direction of connections
    if poly_id == 0:  # Special case: center polygon
        for front_id in directed_poly.all_front:
            tensor_id_front = poly_id_mapping[front_id]
            tensor.add_leg(TensorLeg('I', (tensor_id_front, None)))
    else:
        # Check if there are only left and right neighbors
        has_only_lr_neighbors = has_only_left_right_neighbors(poly_id, directed_polygons)

        # Determine the connection direction (clockwise or counterclockwise)
        if has_only_lr_neighbors:
            # Clockwise direction: right, left, left front, right front
            order = ['right', 'left', 'left_front', 'right_front']
        else:
            # Clockwise direction: back, left, front, right
            order = ['back', 'left', 'front', 'right']

        # Add legs
        for direction in order:
            neighbor_id = getattr(directed_poly, direction, None)
            if neighbor_id is not None:
                tensor_id_nbr = poly_id_mapping[neighbor_id]
                tensor.add_leg(TensorLeg('I', (tensor_id_nbr, None)))
            else:
                tensor.add_leg(TensorLeg('I', None))  # Unconnected leg

    # Add the tensor to the tensor list
    tensor_list.append(tensor)


def generate_tensors_for_all_polys(directed_polygons, poly_id_mapping, tensor_list):
    for poly_id in directed_polygons:
        generate_tensor_with_legs(poly_id, directed_polygons, poly_id_mapping, tensor_list)


def update_tensor_leg_connections(tensor, tensor_list):
    for leg in tensor.legs:
        # Check if the current leg has a connection
        if leg.connection is not None and leg.connection[1] is None:
            connected_tensor_id = leg.connection[0]

            # Get the connected tensor
            connected_tensor = get_tensor_from_id(tensor_list, connected_tensor_id)

            # Find the leg in the connected tensor that connects to the current tensor
            for connected_leg_index, connected_leg in enumerate(connected_tensor.legs):
                if connected_leg.connection is not None and connected_leg.connection[0] == tensor.tensor_id:
                    # Update the connection information for the current leg
                    leg.connection = (connected_tensor_id, connected_leg_index)
                    break


# Iterate through each tensor in tensor_list and update the connection information for its legs
def update_all_tensor_connections(tensor_list):
    for tensor in tensor_list:
        update_tensor_leg_connections(tensor, tensor_list)


def swap_legs_for_same_layer_neighbor(tensor_list):
    for tensor in tensor_list:
        # Iterate through each leg and check if it connects to a neighbor in the same layer
        for i, leg in enumerate(tensor.legs):
            if leg.connection is not None:
                connected_tensor_id = leg.connection[0]
                connected_tensor = get_tensor_from_id(tensor_list, connected_tensor_id)
                if connected_tensor.layer == tensor.layer:  # Found a neighbor in the same layer
                    if i == 1:  # If the second leg connects to a neighbor in the same layer, no action is needed
                        break
                    elif i == 0:  # If the first leg connects to a neighbor in the same layer, swap the legs
                        swap_tensor_legs(tensor, 0, 1, tensor_list)
                        swap_tensor_legs(tensor, 2, 3, tensor_list)
                        break  # After the swap, exit the loop
                    elif i == 3:  # If the fourth leg connects to a neighbor in the same layer, swap the legs
                        swap_tensor_legs(tensor, 1, 3, tensor_list)
