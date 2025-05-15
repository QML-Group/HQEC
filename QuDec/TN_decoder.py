import numpy as np
from OperatorPush.PushingToolbox import batch_push
from OperatorPush.OperatorToolbox import traverse_ups_powers
from QuDec.OperatorProcessor import pauli_to_binary_vector
from QuDec.PauliDecoder import (generate_pauli_error_vector, calculate_syndrome, batch_convert_to_binary_vectors,
                                create_f, binary_vector_to_pauli, apply_mod2_sum, is_error_equivalent)
from QuDec.Mod2Algebra import mod2_matrix_multiply
from QuDec.InputProcessor import extract_stabilizers_from_result_dict, extract_logicals_from_result_dict
import tensornetwork as tn
import psutil
import os
from multiprocessing import Pool

def pauli_to_indices(pauli_string):
    """Convert a Pauli string to a list of indices where I=0, X=1, Y=2, Z=3."""
    pauli_map = {'I': 0, 'X': 1, 'Y': 2, 'Z': 3}
    return [pauli_map[char] for char in pauli_string]


def generate_tensor_array(tensor):
    """
    Generate a numpy array representation of a tensor with dimension origin tracking.

    Args:
    tensor (Tensor): The tensor object containing stabilizers, logical Z and X operators.

    Returns:
    tuple: A numpy array representing the tensor and a list of dimension origins.
    """

    # Determine the size of each dimension
    num_legs = len(tensor.legs)
    dim_size = 4  # 'I', 'X', 'Y', 'Z' (0, 1, 2, 3)

    # Initialize the tensor array
    tensor_array = np.zeros([dim_size] * num_legs)

    # Get all stabilizers including logical operators if they exist
    all_stabilizers = tensor.all_ups

    # Generate all possible stabilizers combinations (ups powers)
    power, all_stabs_list = traverse_ups_powers(all_stabilizers)

    # Fill tensor array
    for stab in all_stabs_list:
        index_tuple = tuple('IXYZ'.index(char) for char in stab)  # Convert stabilizer to index tuple
        tensor_array[index_tuple] = 1

    # Create the dimension origin list
    dimension_origin = [(tensor.tensor_id, leg_index) for leg_index in range(num_legs)]

    return tensor_array, dimension_origin


def collect_network_edges(tensor_list):
    """
    Collect all connections (edges) in the tensor network.

    Args:
    tensor_list (list): List of Tensor objects in the network.

    Returns:
    list: A list of tuples, each representing an edge formatted as:
          (smaller_tensor_id, leg_id_in_smaller_tensor, larger_tensor_id, leg_id_in_larger_tensor)
    """
    edge_set = set()  # Use a set to avoid duplicates

    # Iterate through each tensor and each leg to collect connections
    for tensor in tensor_list:
        for leg_index, leg in enumerate(tensor.legs):
            if leg.connection:
                # Extract connection details
                connected_tensor_id, connected_leg_id = leg.connection
                # Create an edge based on tensor ID order to maintain consistency and avoid duplicates
                smaller_id = min(tensor.tensor_id, connected_tensor_id)
                larger_id = max(tensor.tensor_id, connected_tensor_id)

                if smaller_id == tensor.tensor_id:
                    edge = (smaller_id, leg_index, larger_id, connected_leg_id)
                else:
                    edge = (smaller_id, connected_leg_id, larger_id, leg_index)

                edge_set.add(edge)

    return list(edge_set)


def convert_tensors_to_np_tensors(tensor_list):
    """
    Convert all tensors in the tensor list to their respective NumPy tensor representations.

    Args:
    tensor_list (list): List of Tensor objects.

    Returns:
    dict: A dictionary mapping tensor IDs to their corresponding NumPy tensors.
    """
    np_tensor_dict = {}

    for tensor in tensor_list:
        # print(f"tensor.tensor_id: {tensor.tensor_id}, tensor.all_ups: {tensor.all_ups}")
        # Generate the NumPy tensor for each Tensor object using the generate_tensor_array function
        np_tensor = generate_tensor_array(tensor)
        np_tensor_dict[tensor.tensor_id] = np_tensor

    return np_tensor_dict


def convert_np_tensors_to_tn_nodes(np_tensor_dict):
    """
    Convert all NumPy tensors in the dictionary to their respective tn.Node objects,
    naming each node according to its tensor ID.

    Args:
    np_tensor_dict (dict): Dictionary mapping tensor IDs to their corresponding NumPy tensors.

    Returns:
    dict: A dictionary mapping tensor IDs to their corresponding tn.Node objects, with nodes named by their tensor IDs.
    """
    tn_node_dict = {}

    for tensor_id, np_tensor in np_tensor_dict.items():
        # Create a tn.Node for each NumPy tensor, naming it with its tensor ID
        node = tn.Node(np_tensor[0], name=str(tensor_id))
        tn_node_dict[tensor_id] = node

    return tn_node_dict


def connect_tn_nodes(tn_nodes, edges):
    """
    Connect tensor network nodes based on the provided list of edges, ordered by the higher tensor ID involved
    in each edge, and return a dictionary where each key is the original edge information.

    Args:
    tn_nodes (dict): A dictionary mapping tensor IDs to their respective tn.Node objects.
    edges (list of tuple): List of tuples representing the edges. Each tuple is formatted as
                           (tensor_id_1, leg_id_1, tensor_id_2, leg_id_2).

    Returns:
    dict: A dictionary where keys are tuples (tensor_id_1, leg_id_1, tensor_id_2, leg_id_2) representing
          the original edge information, and values are the tn.Edge objects representing the connections made.
    """
    # Sort edges based on the maximum tensor ID involved, descending
    edges_sorted = sorted(edges, key=lambda x: max(x[0], x[2]), reverse=True)

    tn_edges = {}

    for tensor_id_1, leg_id_1, tensor_id_2, leg_id_2 in edges_sorted:
        # Fetch the respective nodes
        node1 = tn_nodes[tensor_id_1]
        node2 = tn_nodes[tensor_id_2]

        # Connect the specified legs of the nodes
        edge = node1[leg_id_1] ^ node2[leg_id_2]
        tn_edges[(tensor_id_1, leg_id_1, tensor_id_2, leg_id_2)] = edge

    return tn_edges


def contract_tn_edges(edges):
    """
    Contract a dictionary of tensor network edges sequentially and return the final tensor network node.

    Args:
    edges (dict): A dictionary of edges to be contracted, keyed by tuples containing tensor and leg IDs.

    Returns:
    tn.Node: The final tensor network node resulting from the contraction of all edges.
    """
    # Convert edges dict to a list for easier manipulation
    edge_list = list(edges.values())

    while len(edge_list) > 0:
        # Pop the first edge from the list
        edge_to_contract = edge_list.pop(0)
        # print(f"Contracting edge between {edge_to_contract.node1.name} and {edge_to_contract.node2.name}")
        # print(f"Node1 shape: {edge_to_contract.node1.tensor.shape}")
        # print(f"Node2 shape: {edge_to_contract.node2.tensor.shape}")

        # Contract this edge
        if edge_to_contract.node1 == edge_to_contract.node2:
            new_nodes_name = edge_to_contract.node1.name
        else:
            new_nodes_name = f"{edge_to_contract.node1.name if edge_to_contract.node1.name != '__unnamed_node__' else ''}{'_' if edge_to_contract.node1.name and edge_to_contract.node2.name != '__unnamed_node__' else ''}{edge_to_contract.node2.name if edge_to_contract.node2.name != '__unnamed_node__' else ''}"

        new_node = tn.contract(edge_to_contract)
        new_node.set_name(new_nodes_name)

        # After contracting, check for any new edges formed and whether they need to be contracted further
        # for new_edge in new_node.edges:
        #     if not new_edge.is_dangling() and new_edge not in edge_list:
        #         edge_list.append(new_edge)

    # After all contractions, return the final node regardless of the state of its edges
    return new_node


def collect_edges_during_backtrack(tensor_list, starting_tensor_id=0, logger_mode=False):
    # Prepare a list to store edge information
    edges_during_backtrack = []
    visited_tensors = set()

    # Start from the starting_tensor_id to visit and collect edges
    recursively_collect_edges(tensor_list, starting_tensor_id, None, visited_tensors,
                              edges_during_backtrack, logger_mode=logger_mode)

    # Return the collected edge information
    return edges_during_backtrack

def recursively_collect_edges(tensor_list, current_tensor_id, previous_tensor_id, visited_tensors,
                              edges_during_backtrack, logger_mode=False):
    # Get the current tensor
    # print(f"Visiting: {current_tensor_id}")
    current_tensor = get_tensor_from_id(tensor_list, current_tensor_id)
    visited_tensors.add(current_tensor_id)

    # Record edges as we prepare to backtrack
    neighbor_ids = current_tensor.get_connections()
    # print(f"neighbor_ids:{neighbor_ids}")
    for neighbor_id in neighbor_ids:
        if neighbor_id in visited_tensors:
            # Avoid revisiting tensors
            continue

        neighbor_tensor = get_tensor_from_id(tensor_list, neighbor_id)
        # Compare layers to determine the direction of traversal
        if neighbor_tensor.layer >= current_tensor.layer:
            # Only traverse to tensors of higher or same layer
            recursively_collect_edges(tensor_list, neighbor_id, current_tensor_id, visited_tensors,
                                      edges_during_backtrack, logger_mode)
    # print(f"BACK, id {current_tensor_id}")
    # On backtracking, collect the edge information
    if previous_tensor_id is not None:
        for current_leg_id, current_leg in enumerate(current_tensor.legs):
            if current_leg.connection is not None:
                if current_leg.connection[0] == previous_tensor_id:
                    previous_tensor_leg_id = current_leg.connection[1]
                    if current_tensor_id < previous_tensor_id:
                        edge_info = (current_tensor_id, current_leg_id, previous_tensor_id, previous_tensor_leg_id)
                        edges_during_backtrack.append(edge_info)
                    else:
                        edge_info = (previous_tensor_id, previous_tensor_leg_id, current_tensor_id, current_leg_id)
                        edges_during_backtrack.append(edge_info)
                    if logger_mode:
                        print(f"Backtracking through edge: {edge_info}")


def get_tensor_from_id(tensor_list, tensor_id):
    # Mock function to return a tensor from a list
    return next((tensor for tensor in tensor_list if tensor.tensor_id == tensor_id), None)


def contract_self_edges(node):
    """
    Contract self-connected edges of a tensor network node.

    Args:
    node (tn.Node): A tensor network node whose self-connected edges need to be contracted.

    Returns:
    tn.Node: The tensor network node after contracting any self-connected edges.
    """
    while True:
        newly_contracted = False
        # Identify self-connected edges
        for edge in node.edges:
            if not edge.is_dangling() and edge.node1 == edge.node2:
                # This edge is a self-loop
                node_name = node.name
                node = tn.contract(edge, name=node_name)
                newly_contracted = True
                break
        if not newly_contracted:
            break
    return node


def collect_boundary_leg_ids(tensor_list, starting_tensor_id=0, logger_mode=False):
    # Create a list to store leg identifiers
    boundary_leg_ids = []
    visited_tensors = set()
    deeply_visited_tensors = set()

    # Start from starting_tensor_id to visit and collect leg ids
    recursively_collect_boundary_leg_ids(tensor_list, starting_tensor_id, visited_tensors, boundary_leg_ids,
                                         deeply_visited_tensors, logger_mode=logger_mode)

    # Return the collected leg identifiers
    return boundary_leg_ids


def recursively_collect_boundary_leg_ids(tensor_list, current_tensor_id, visited_tensors, boundary_leg_ids,
                                         deeply_visited_tensors, logger_mode=False):
    # Get the current tensor
    if logger_mode:
        print(f"Visiting: {current_tensor_id}")
    current_tensor = get_tensor_from_id(tensor_list, current_tensor_id)
    visited_tensors.add(current_tensor_id)

    # Check if the tensor has dangling legs and has not been visited yet, if true, then collect leg ids
    if current_tensor.dangling_leg_num() > 0 and (current_tensor not in deeply_visited_tensors):
        # Collect leg ids of this tensor
        for leg_id, leg in enumerate(current_tensor.legs):
            if leg.connection is None and not leg.logical:  # Dangling leg
                boundary_leg_ids.append((current_tensor_id, leg_id))
                if logger_mode:
                    print(f"Collected leg id: {(current_tensor_id, leg_id)} from tensor {current_tensor_id}")

    # Determine the next tensor to visit
    neighbor_ids = current_tensor.get_connections()
    higher_layer_neighbor_ids = []
    for neighbor_id in neighbor_ids:
        if neighbor_id in visited_tensors or neighbor_id in deeply_visited_tensors:
            continue
        neighbor_tensor = get_tensor_from_id(tensor_list, neighbor_id)
        if neighbor_tensor.layer >= current_tensor.layer:
            higher_layer_neighbor_ids.append(neighbor_id)

    # Sort neighbor tensors by layer to prioritize visiting higher layers first
    sorted_neighbors = sorted(higher_layer_neighbor_ids, key=lambda x: get_tensor_from_id(tensor_list, x).layer,
                              reverse=True)

    for next_tensor_id in sorted_neighbors:
        recursively_collect_boundary_leg_ids(tensor_list, next_tensor_id, visited_tensors, boundary_leg_ids,
                                             deeply_visited_tensors, logger_mode)

    deeply_visited_tensors.add(current_tensor_id)


def create_bound_vector_tensor_node(p, rx, ry, rz, pauli_char):
    """
    Create a tensor node with a boundary condition vector based on probabilities associated with Pauli errors.

    Args:
    p (float): Probability of an error occurring.
    rx (float): Relative probability of an X error given an error occurs.
    ry (float): Relative probability of a Y error given an error occurs.
    rz (float): Relative probability of a Z error given an error occurs.
    pauli_char (str): Pauli character ('I', 'X', 'Y', 'Z') indicating the base state.

    Returns:
    tn.Node: Tensor network node representing the boundary condition.
    """
    if pauli_char == 'I':
        p_vec = np.array([1 - p, p * rx, p * ry, p * rz])
    elif pauli_char == 'X':
        p_vec = np.array([p * rx, 1 - p, p * rz, p * ry])
    elif pauli_char == 'Y':
        p_vec = np.array([p * ry, p * rz, 1 - p, p * rx])
    elif pauli_char == 'Z':
        p_vec = np.array([p * rz, p * ry, p * rx, 1 - p])
    else:
        raise ValueError("Invalid Pauli character. Must be one of 'I', 'X', 'Y', 'Z'.")

    # Create the tensor network node with this vector
    # boundary_node = tn.Node(p_vec, name=f"Boundary_{pauli_char}")
    boundary_node = tn.Node(p_vec)
    return boundary_node


def add_boundary_conditions_to_dangling_edges(tn_nodes, boundary_leg_ids, s_pauli, p, rx, ry, rz):
    """
    Attach a boundary condition to each dangling edge specified in boundary_leg_ids, using the provided
    probabilities and Pauli operators from s_pauli.

    Args:
    tn_nodes (dict): Dictionary of tensor network nodes, keyed by tensor_id.
    boundary_leg_ids (list of tuple): List of tuples (tensor_id, leg_id) identifying dangling edges.
    s_pauli (str): String of Pauli operators for each dangling edge in boundary_leg_ids.
    p (float): Overall error probability.
    rx, ry, rz (float): Probabilities for X, Y, Z errors, satisfying rx + ry + rz = 1.

    Returns:
    dict: Dictionary of newly created tensor network edges, keyed by (tensor_id, leg_id).
    """
    new_edges = {}

    for index, (tensor_id, leg_id) in enumerate(boundary_leg_ids):
        pauli_char = s_pauli[index]
        # Create boundary vector tensor node based on the Pauli character
        boundary_node = create_bound_vector_tensor_node(p, rx, ry, rz, pauli_char)

        # Connect the boundary node to the dangling edge of the tensor
        if leg_id < len(tn_nodes[tensor_id].edges) and tn_nodes[tensor_id].edges[leg_id].is_dangling():
            edge = tn_nodes[tensor_id].edges[leg_id] ^ boundary_node[0]
            new_edges[(tensor_id, leg_id)] = edge

    return new_edges


def normalize_tensor_node(node):
    """
    Normalize the tensor within a tensor network node in place.

    Args:
    node (tn.Node): A tensor network node whose tensor is to be normalized.

    Returns:
    tn.Node: The same node with its tensor normalized.
    """
    tensor_sum = np.sum(node.tensor)
    if tensor_sum != 0:
        node.tensor /= tensor_sum
    return node


def tn_quantum_error_correction_decoder_multiprocess(tensor_list, p, rx, ry, rz, N, stabilizers=None, logical_x=None,
                                                     logical_z=None, n_process=1, cpu_affinity_list=None, f=None):
    if stabilizers is None or logical_z is None or logical_x is None:
        results_dict = batch_push(tensor_list)
        stabilizers = extract_stabilizers_from_result_dict(results_dict)
        logical_zs, logical_xs = extract_logicals_from_result_dict(results_dict)
        logical_z = logical_zs[0]
        logical_x = logical_xs[0]

    stabilizers_binary = batch_convert_to_binary_vectors(stabilizers)
    stabilizer_matrix = np.array(stabilizers_binary)
    n = len(stabilizers[0])

    if f is None:
        f = create_f(symplectic_stabilizers=stabilizers_binary)

    args = [(tensor_list, p, rx, ry, rz, f, n, stabilizers, stabilizer_matrix, logical_z, logical_x, cpu_affinity_list)
            for _ in range(N)]

    successful_decodings = 0
    with Pool(n_process) as pool:
        results = pool.starmap(tensor_network_decoding_iteration, args)
        successful_decodings = sum(results)

    success_rate = successful_decodings / N
    return success_rate


def tensor_network_decoding_iteration(tensor_list, p, rx, ry, rz, f, n, stabilizers, stabilizer_matrix, logical_z,
                                      logical_x, affinity=None):
    # Set CPU affinity for the process if specified
    if affinity is not None:
        process_ = psutil.Process(os.getpid())
        process_.cpu_affinity(affinity)

    e_0 = generate_pauli_error_vector(px=p * rx, py=p * ry, pz=p * rz, n=n)
    y = calculate_syndrome(stabilizer_matrix, e_0)

    e = mod2_matrix_multiply(f, y)
    str_e = binary_vector_to_pauli(binary_vector=e)

    str_e_bar = tensor_network_decoder(tensor_list, p, rx, ry, rz, str_e, e, logical_z, logical_x)
    e_bar = pauli_to_binary_vector(str_e_bar)

    # Compare the estimated error with the actual error
    is_successful = is_error_equivalent(stabilizers, e_0, e_bar)
    return is_successful


def tensor_network_decoder(tensor_list, p, rx, ry, rz, str_e, e, logical_z, logical_x):
    boundary_leg_ids = collect_boundary_leg_ids(tensor_list, starting_tensor_id=0)
    edges_during_backtrack = collect_edges_during_backtrack(tensor_list, starting_tensor_id=0, logger_mode=False)
    edges = collect_network_edges(tensor_list)
    np_tensor_dict = convert_tensors_to_np_tensors(tensor_list)
    tn_nodes = convert_np_tensors_to_tn_nodes(np_tensor_dict)
    connected_edges = connect_tn_nodes(tn_nodes, edges)

    bound_connected_edges = add_boundary_conditions_to_dangling_edges(tn_nodes=tn_nodes,
                                                                      boundary_leg_ids=boundary_leg_ids,
                                                                      s_pauli=str_e, p=p, rx=rx, ry=ry, rz=rz)
    new_node = contract_tn_edges(bound_connected_edges)
    for edge_key in edges_during_backtrack:
        if connected_edges[edge_key].node1.name == connected_edges[edge_key].node2.name:
            new_nodes_name = connected_edges[edge_key].node1.name
        else:
            new_nodes_name = f"{connected_edges[edge_key].node1.name if connected_edges[edge_key].node1.name != '__unnamed_node__' else ''}{'_' if connected_edges[edge_key].node1.name and connected_edges[edge_key].node2.name != '__unnamed_node__' else ''}{connected_edges[edge_key].node2.name if connected_edges[edge_key].node2.name != '__unnamed_node__' else ''}"

        new_node = tn.contract(connected_edges[edge_key])
        new_node.set_name(new_nodes_name)
        new_node = contract_self_edges(new_node)
        new_node = normalize_tensor_node(new_node)

    ml_coset = np.argmax(new_node.tensor)
    if ml_coset == 0:
        return str_e
    elif ml_coset == 1:
        logical_x_binary = pauli_to_binary_vector(logical_x)
        xe = apply_mod2_sum(e, [logical_x_binary], [1])
        str_xe = binary_vector_to_pauli(xe)
        return str_xe
    elif ml_coset == 2:
        logical_x_binary = pauli_to_binary_vector(logical_x)
        logical_z_binary = pauli_to_binary_vector(logical_z)
        ye = apply_mod2_sum(e, [logical_x_binary, logical_z_binary], [1, 1])
        str_ye = binary_vector_to_pauli(ye)
        return str_ye
    else:
        logical_z_binary = pauli_to_binary_vector(logical_z)
        ze = apply_mod2_sum(e, [logical_z_binary], [1])
        str_ze = binary_vector_to_pauli(ze)
        return str_ze
