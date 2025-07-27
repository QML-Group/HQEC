from LEGO_HQEC.OperatorPush.OperatorToolbox import pauli_product, traverse_ups_powers, pauli_flip
import logging

# Config logging
logging.basicConfig(filename='OperatorPush.log', level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Create a logger
logger = logging.getLogger('TensorTool')


class TensorLeg:
    def __init__(self, operator, connection=None):
        self.operator = operator  # Store the operator ('I', 'X', 'Y', 'Z')
        self.connection = connection  # Store the connection information,
        # a tuple (connected tensor's number, corresponding tensor's leg number)
        self.blocked = False
        self.logical = False  # Logical, by default: False
        self.clifford_gate = None
        self.already_read = False

    def __str__(self):
        return f"Operator: {self.operator}, Connection: {self.connection}, Blocked: {self.blocked}, " \
               f"Logical: {self.logical}, clifford: {self.clifford_gate}, already_read: {self.already_read}"

    def operator_set(self, operator):
        self.operator = operator


class Tensor:
    def __init__(self, tensor_id, num_legs):
        self.tensor_id = tensor_id
        self.legs = [TensorLeg('I') for _ in range(num_legs)]
        self.ups_list = []  # Store the complete set of generators for the ups group
        self.starting_tensor = False
        self.layer = None
        self.stabilizer_list = []  # List to store stabilizer UPS
        self.logical_z_list = []  # List to store logical Z UPS
        self.logical_x_list = []  # List to store logical X UPS
        self.all_ups = []
        self.incomplete_logical = False

    def set_leg(self, leg_index, operator, connection):
        if 0 <= leg_index < len(self.legs):
            self.legs[leg_index] = TensorLeg(operator, connection)
        else:
            logger.error("Invalid leg index")

    def add_leg(self, leg=None):
        if leg is None:
            new_leg = TensorLeg('I')
            self.legs.append(new_leg)
        else:
            new_leg = leg
            self.legs.append(new_leg)

    def pauli_push(self, leg_index, tensor_list, logger_mode=False):
        if 0 <= leg_index < len(self.legs):
            current_leg = self.legs[leg_index]

            # Check if there are non-'I' operators on the current leg.
            if current_leg.operator != 'I':
                connection = current_leg.connection
                if connection is not None:
                    target_tensor_index, target_leg_index = connection

                    # Ensure the target tensor exists.
                    target_tensor = None
                    for target in tensor_list:
                        if target.tensor_id == target_tensor_index:
                            target_tensor = target
                            break
                    if target_tensor is not None:

                        # Ensure the target leg exists.
                        if 0 <= target_leg_index < len(target_tensor.legs):
                            target_leg = target_tensor.legs[target_leg_index]
                            # Mark the original operator
                            origin_operator = current_leg.operator

                            # Check clifford gate
                            if current_leg.clifford_gate == 'H':
                                current_leg.operator = pauli_flip(current_leg.operator)

                            # Move the operator.
                            target_leg_origin_operator = target_leg.operator
                            target_leg.operator = pauli_product([current_leg.operator, target_leg.operator])
                            current_leg.operator = 'I'
                            if logger_mode:
                                logger.info(f"Pauli push: Operator '{origin_operator}' of tensor "
                                            f"{self.tensor_id} pushed to target leg {target_leg_index} "
                                            f"of tensor {target_tensor_index}, target leg's original operator: "
                                            f"'{target_leg_origin_operator}', result operator: '{target_leg.operator}'")

                        else:
                            if logger_mode:
                                logger.error("Invalid target leg index")
                    else:
                        if logger_mode:
                            logger.error("Invalid target tensor index")
                else:
                    if logger_mode:
                        logger.error("Current leg is not connected to any other leg")
            else:
                if logger_mode:
                    logger.error("Current leg operator is 'I'")
        else:
            if logger_mode:
                logger.error("Invalid leg index")

    def __str__(self):
        leg_info = "\n".join([f"Leg {i}: {leg}" for i, leg in enumerate(self.legs)])
        return f"Tensor ID: {self.tensor_id}, layer:{self.layer}\nstabilizer: {self.stabilizer_list}\nlogical z" \
               f":{self.logical_z_list}\nlogical x :{self.logical_x_list}\nUPS_list:{self.ups_list}\n{leg_info}"

    def get_connections(self):
        """
        Get the tensor IDs of all connected tensors.

        Args:
        - tensor_list: The list of all tensors.

        Returns:
        - connected_tensor_ids: A list of tensor IDs connected to this tensor.
        """
        connected_tensor_ids = []

        for leg in self.legs:
            if leg.connection is not None:
                connected_tensor_id, _ = leg.connection
                if connected_tensor_id not in connected_tensor_ids:
                    connected_tensor_ids.append(connected_tensor_id)

        return connected_tensor_ids

    def ups_decision(self, legs_for_ups_push, logger_mode=False):
        if len(self.ups_list) == 0:
            if logger_mode:
                logger.error(f"ups Not Assigned for tensor {self.tensor_id}")
        # Initialize a variable to store the selected ups
        selected_ups = None
        logical_legs_list = [leg for leg in range(len(self.legs)) if self.legs[leg].logical]

        # Find the corresponding ups generator, with I on logical leg
        for ups_generator in self.ups_list:
            ups_matched = True
            # Iterate over the legs for ups push
            for leg_index in legs_for_ups_push:
                leg = self.legs[leg_index]
                operator = leg.operator
                if operator != ups_generator[leg_index]:
                    ups_matched = False
            if ups_matched:
                identity_logical_leg = True
                for logical_index in logical_legs_list:
                    if ups_generator[logical_index] != 'I' and not self.incomplete_logical:
                        identity_logical_leg = False
                if identity_logical_leg:
                    selected_ups = ups_generator
                    break

        # Check if a ups was found
        if selected_ups is not None:
            if logger_mode:
                logger.info(f'ups selected in generator set, selected_ups = {selected_ups}')
            return selected_ups  # Return the selected ups

        # If no matching ups was found in generators, expand the full ups group and search for a matching ups.
        power, full_ups = traverse_ups_powers(self.ups_list)
        selected_power = None

        # We still prefer ups with only I, X, Z (and I on logical leg),
        # so firstly check if there's a matching ups with only I, X, Z with I on logical leg
        for i in range(len(full_ups)):
            ups_matched = True
            ups = full_ups[i]
            # Iterate over the legs for ups push
            for leg_index in legs_for_ups_push:
                leg = self.legs[leg_index]
                operator = leg.operator
                if operator != ups[leg_index]:
                    ups_matched = False
            if ups_matched and 'Y' not in ups:
                identity_logical_leg = True
                for logical_index in logical_legs_list:
                    if ups[logical_index] != 'I' and not self.incomplete_logical:
                        identity_logical_leg = False
                if identity_logical_leg:
                    selected_ups = ups
                    # Get the power of the selected ups
                    selected_power = power[i]
                    break

        # Check if a ups was found
        if selected_ups is not None:
            if logger_mode:
                logger.info(f'ups selected from the whole group, selected_ups = {selected_ups}, '
                            f'power = {selected_power}')
            return selected_ups  # Return the selected ups

        # If there's no matching ups with only I, X, Z, then search the full group (I on logical leg)
        for i in range(len(full_ups)):
            ups_matched = True
            ups = full_ups[i]
            # Iterate over the legs for ups push
            for leg_index in legs_for_ups_push:
                leg = self.legs[leg_index]
                operator = leg.operator
                if operator != ups[leg_index]:
                    ups_matched = False
            if ups_matched:
                identity_logical_leg = True
                for logical_index in logical_legs_list:
                    if ups[logical_index] != 'I' and not self.incomplete_logical:
                        identity_logical_leg = False
                if identity_logical_leg:
                    selected_ups = ups
                    # Get the power of the selected ups
                    selected_power = power[i]
                    break

        # Check if a ups was found
        if selected_ups is not None:
            if logger_mode:
                logger.info(f'ups selected from the whole group, selected_ups = {selected_ups},'
                            f' power = {selected_power}')
            return selected_ups  # Return the selected ups

        return None  # Return None if no matching ups was found

    # This function is part of the Tensor class and can be called as follows:
    # selected_ups = self.ups_decision(legs_for_ups_push, tensor_list)

    def is_ups_condition_met(self):
        non_i = False
        for leg in self.legs:
            if leg.logical:
                continue
            if leg.operator != 'I':
                if leg.connection is not None:
                    if not leg.blocked:
                        return False  # Non-'I' legs that are not blocked do not meet the condition.
                non_i = True
        if non_i:
            return True
        return False

    def operator_push_decision(self, tensor_list, tensors_for_current_round, logger_mode=False):
        if logger_mode:
            logger.info(f'\nWorking on tensor: {self.tensor_id}')
        # Step 1: Check for non-I operators
        non_i_legs = [i for i, leg in enumerate(self.legs) if leg.operator != 'I']

        # Step 2: Pauli push
        for leg_index in non_i_legs:
            leg = self.legs[leg_index]
            if leg.connection is not None and not leg.blocked:
                self.pauli_push(leg_index, tensor_list, logger_mode=logger_mode)

        if self.starting_tensor:
            same_layer_neighbor_tensor = self.find_same_layer_neighbor(tensors_for_current_round)
            if same_layer_neighbor_tensor:
                for leg_index in non_i_legs:
                    if self.legs[leg_index].connection is not None:
                        if self.legs[leg_index].connection[0] == same_layer_neighbor_tensor[0]:
                            self.pauli_push(leg_index, tensor_list, logger_mode=logger_mode)
            for leg_index in range(len(self.legs)):
                self.block_leg(leg_index, tensor_list)
            # Block legs
            if same_layer_neighbor_tensor:
                return same_layer_neighbor_tensor
            return
        # Step 3: Re-check for non-I operators and ups condition
        # Check for ups condition
        if not self.is_ups_condition_met():
            if logger_mode:
                logger.info(f'ups push condition not met, skipping ups push for tensor {self.tensor_id}')
            for leg_index in range(len(self.legs)):
                self.block_leg(leg_index, tensor_list)
            return
        if logger_mode:
            logger.info(f'ups push condition met, executing ups push for tensor {self.tensor_id}')
        # If ups condition is met, then collect the leg operators that need to be pushed by ups
        legs_for_ups_push = [i for i, leg in enumerate(self.legs) if leg.blocked]

        # Initialize an empty list to store operators
        operators_on_legs_for_ups_push = []

        # Iterate over the leg IDs in legs_for_ups_push
        for leg_id in legs_for_ups_push:
            leg = self.legs[leg_id]
            operator = leg.operator
            operators_on_legs_for_ups_push.append(operator)
        if logger_mode:
            logger.info(f"Collected legs for ups push for tensor {self.tensor_id}: {legs_for_ups_push},"
                        f" corresponding operator:, {operators_on_legs_for_ups_push}")

        # Step 4: Call the ups_decision function and apply the selected ups
        selected_ups = self.ups_decision(legs_for_ups_push, logger_mode=logger_mode)

        # If selected_ups is none, then ask same layer neighbor for a helping hand, before that, reconsider for a
        # simpler ups (without considering the leg that connects to the same layer neighbor, and push pauli to same
        # layer neighbor and next layer (if there's a next layer), and return a signal for push function to add its
        # neighbor into the queue.
        if selected_ups is None:
            same_layer_neighbor_tensor = self.find_same_layer_neighbor(tensors_for_current_round)
            if logger_mode:
                logger.info(f"ups not found, call ups reconsider and send operator to same-layer neighbor"
                            f" {same_layer_neighbor_tensor[0]}")
            for leg_num in range(len(self.legs)):
                if self.legs[leg_num].connection is None:
                    break
                if self.legs[leg_num].connection[0] == same_layer_neighbor_tensor[0]:
                    if self.legs[leg_num].operator != "I":
                        self.pauli_push(leg_num, tensor_list, logger_mode=logger_mode)
                    legs_for_ups_push.remove(leg_num)
            # Check if there's non I operator
            non_i_op = False
            for leg_id in legs_for_ups_push:
                if self.legs[leg_id].operator != 'I':
                    non_i_op = True
            if not non_i_op:
                return None
            reselected_ups = self.ups_decision(legs_for_ups_push, logger_mode=logger_mode)
            if reselected_ups is None:
                return None
            self.apply_operators_to_legs(reselected_ups, logger_mode=logger_mode)
            # Do pauli push
            non_i_legs = [i for i, leg in enumerate(self.legs) if leg.operator != 'I']
            if not non_i_legs:
                if logger_mode:
                    logger.info(f'No non-I leg for tensor {self.tensor_id} after ups push')
            else:
                for leg_index in non_i_legs:
                    leg = self.legs[leg_index]
                    if leg.connection is not None:
                        self.pauli_push(leg_index, tensor_list, logger_mode=logger_mode)
            # Block legs
            for leg_index in range(len(self.legs)):
                self.block_leg(leg_index, tensor_list)
            return same_layer_neighbor_tensor

        # If selected_ups is found, then apply it.
        self.apply_operators_to_legs(selected_ups, logger_mode=logger_mode)

        # Step 5: new round of pauli push
        non_i_legs = [i for i, leg in enumerate(self.legs) if leg.operator != 'I']
        if not non_i_legs:
            if logger_mode:
                logger.info(f'No non-I leg for tensor {self.tensor_id} after ups push')
        else:
            for leg_index in non_i_legs:
                leg = self.legs[leg_index]
                if leg.connection is not None and not leg.blocked:
                    self.pauli_push(leg_index, tensor_list, logger_mode=logger_mode)

        # Step 6: block all connected legs
        for leg_index in range(len(self.legs)):
            self.block_leg(leg_index, tensor_list)
        return None


    def find_same_layer_neighbor(self, tensors_for_current_round):
        neighbors_id_set = set(self.get_connections())
        same_layer_tensor_id_set = set(tensors_for_current_round)
        same_layer_neighbor_tensor_id = list(neighbors_id_set.intersection(same_layer_tensor_id_set))
        return same_layer_neighbor_tensor_id

    def block_leg(self, leg_index, tensor_list):
        # Check if the leg index is valid.
        if 0 <= leg_index < len(self.legs):
            leg = self.legs[leg_index]

            # Check if the leg has a connection and is not blocked.
            if leg.connection is not None and not leg.blocked:
                leg.blocked = True
                for target_tensor in tensor_list:
                    if target_tensor.tensor_id == leg.connection[0]:
                        target_leg = target_tensor.legs[leg.connection[1]]
                        target_leg.blocked = True
                        break

    def apply_operators_to_legs(self, operator_list, logger_mode=False):
        # Check if the operator list length matches the number of legs in the tensor.
        if len(operator_list) != len(self.legs):
            if logger_mode:
                logger.error("Operator list length does not match the number of legs.")
            return

        # Apply operators to each leg.
        for i, pauli_operator in enumerate(operator_list):
            self.legs[i].operator = pauli_product([self.legs[i].operator, pauli_operator])

    def dangling_leg_num(self):
        connected_leg_number = len(self.get_connections())
        non_logical_leg_number = self.non_logical_leg_num()
        dangling_leg_number = non_logical_leg_number - connected_leg_number
        return dangling_leg_number

    def non_logical_leg_num(self):
        non_logical_leg_num = 0
        for leg in self.legs:
            if not leg.logical:
                non_logical_leg_num += 1
        return non_logical_leg_num


def create_cell_centered_topology(grg, selected_ids, tensor_list):
    n_tensor = len(grg)

    for tensor_id in range(n_tensor):
        if tensor_id in selected_ids:
            if not tensor_exists(tensor_id, tensor_list):
                tensor = Tensor(tensor_id, 0)
                tensor_list.append(tensor)

    for current_tensor_id in selected_ids:
        neighbors = grg[current_tensor_id]

        for target_tensor_id in neighbors:
            if target_tensor_id in selected_ids:
                current_tensor = tensor_list[current_tensor_id]
                target_tensor = tensor_list[target_tensor_id]

                if not are_tensors_connected(current_tensor, target_tensor):
                    current_tensor.add_leg()
                    target_tensor.add_leg()

                    current_leg_index = len(current_tensor.legs) - 1
                    target_leg_index = len(target_tensor.legs) - 1
                    current_tensor.set_leg(current_leg_index, 'I', (target_tensor_id, target_leg_index))
                    target_tensor.set_leg(target_leg_index, 'I', (current_tensor_id, current_leg_index))


def tensor_exists(tensor_id, tensor_list):
    # Check if a tensor with the given ID already exists in the list
    for tensor in tensor_list:
        if tensor.tensor_id == tensor_id:
            return True
    return False


def are_tensors_connected(tensor1, tensor2):
    # Check if the tensors have a leg connection to each other
    for leg in tensor1.legs:
        if leg.connection and leg.connection[0] == tensor2.tensor_id:
            return True
    return False


def create_topology_by_segments(grg):
    tensor_list = []
    n_tensor = len(grg)
    neighbors_of_central_tensor = grg[0]
    for i in range(len(neighbors_of_central_tensor)):
        start = neighbors_of_central_tensor[i]
        if i < len(neighbors_of_central_tensor) - 1:
            end = neighbors_of_central_tensor[i+1]
        else:
            end = n_tensor
        selected_ids = [0] + list(range(start, end))
        create_cell_centered_topology(grg, selected_ids, tensor_list)
    create_cell_centered_topology(grg, list(range(n_tensor)), tensor_list)
    return tensor_list


def add_logical_legs(tensor_list, start_idx, end_idx):
    for tensor in tensor_list[start_idx:end_idx]:
        tensor.add_leg()  # Add a new leg
        new_leg_index = len(tensor.legs) - 1
        tensor.set_leg(new_leg_index, 'I', None)  # No connection, 'I' operator
        tensor.legs[new_leg_index].logical = True  # Set the Logical property to True


def read_out_boundary(tensor_list, starting_tensor_id=0, logger_mode=False):
    # Create a list to store leg information
    boundary_operators = []
    have_been_read_tensors = set()
    have_been_deeply_visited_tensors = set()

    # Start from starting_tensor_id to visit and read out
    recursively_visit_near_boundary_tensor(tensor_list, starting_tensor_id, have_been_read_tensors, boundary_operators,
                                           have_been_deeply_visited_tensors, logger_mode=logger_mode)

    # Return the read out result
    boundary_operators_string = ''.join(boundary_operators)
    return boundary_operators_string


def ensure_minimum_legs(tensor_list, target_leg_number, start_idx, end_idx):
    for tensor in tensor_list[start_idx:end_idx]:
        while len(tensor.legs) < target_leg_number:
            tensor.add_leg()


def add_logical_legs(tensor_list, start_idx, end_idx):
    for tensor in tensor_list[start_idx:end_idx]:
        tensor.add_leg()  # Add a new leg
        new_leg_index = len(tensor.legs) - 1
        tensor.set_leg(new_leg_index, 'I', None)  # No connection, 'I' operator
        tensor.legs[new_leg_index].logical = True  # Set the Logical property to True


def recursively_visit_near_boundary_tensor(tensor_list, given_tensor_id, have_been_read_tensors, boundary_operators,
                                           have_been_deeply_visited_tensors, logger_mode=False):
    # print(f"given_tensor_id, {given_tensor_id}")
    # Get the current tensor
    if logger_mode:
        logger.info(f"visiting: {given_tensor_id}")
    current_tensor = get_tensor_from_id(tensor_list, given_tensor_id)
    # visited_tensors.add(given_tensor_id)

    # Check if the tensor has dangling legs and has not been read yet, if true, then read
    if current_tensor.dangling_leg_num() > 0 and (current_tensor not in have_been_read_tensors):
        # Read out this tensor
        read_leg_operator_on_tensor(tensor_list, given_tensor_id, boundary_operators, have_been_read_tensors,
                                    logger_mode=logger_mode)

    # Pick the next tensor to be visited
    neighbor_ids = current_tensor.get_connections()
    prefer_to_visit_tensor_id_list = list()
    highest_layer_num = 0
    for neighbor_id in neighbor_ids:
        if neighbor_id in have_been_read_tensors or neighbor_id in have_been_deeply_visited_tensors:
            continue
        neighbor_tensor = get_tensor_from_id(tensor_list, neighbor_id)
        current_neighbor_tensor_layer = neighbor_tensor.layer
        if current_neighbor_tensor_layer > highest_layer_num:
            prefer_to_visit_tensor_id_list = list()
            highest_layer_num = current_neighbor_tensor_layer
            prefer_to_visit_tensor_id_list.append(neighbor_id)
        elif current_neighbor_tensor_layer == highest_layer_num:
            prefer_to_visit_tensor_id_list.append(neighbor_id)
    if highest_layer_num == current_tensor.layer:
        return
    if prefer_to_visit_tensor_id_list:
        # Choose the smallest leg id to start with
        for leg_id, current_leg in enumerate(current_tensor.legs):
            if current_leg.connection is not None:
                if current_leg.connection[0] in prefer_to_visit_tensor_id_list and \
                        current_leg.connection[0] not in have_been_read_tensors and \
                        current_leg.connection[0] not in have_been_deeply_visited_tensors:
                    next_tensor_id = current_leg.connection[0]
                    next_tensor = get_tensor_from_id(tensor_list, next_tensor_id)
                    next_tensor_layer = next_tensor.layer
                    if next_tensor_layer < current_tensor.layer:
                        have_been_deeply_visited_tensors.add(given_tensor_id)
                        return
                    else:
                        recursively_visit_near_boundary_tensor(tensor_list, next_tensor_id, have_been_read_tensors,
                                                               boundary_operators, have_been_deeply_visited_tensors,
                                                               logger_mode)
    else:
        return


def read_leg_operator_on_tensor(tensor_list, given_tensor_id, boundary_operators, have_been_read_tensors,
                                logger_mode=False):
    if logger_mode:
        logger.info(f"reading: {given_tensor_id}")
    have_been_read_tensors.add(given_tensor_id)
    # Get the tensor to read out
    current_tensor = get_tensor_from_id(tensor_list, given_tensor_id)
    for leg in current_tensor.legs:
        # Check if the leg meets the conditions (not blocked and not logical)
        if (leg.connection is None) and not leg.logical:
            # Save the operator and leg information
            boundary_operators.append(leg.operator)
            leg.already_read = True


def reading_boundary_complete(tensor_list):
    for current_tensor in tensor_list:
        for current_leg in current_tensor.legs:
            if current_leg.connection is None and not current_leg.logical and not current_leg.already_read:
                return False
    return True


def read_out_logical(tensor_list):
    # Create a list to store leg information
    leg_info = []

    # Traverse each tensor in the tensor_list
    for tensor_id, tensor in enumerate(tensor_list):
        for leg_id, leg in enumerate(tensor.legs):
            # Check if the leg meets the conditions (logical)
            if leg.logical:
                # Save the operator and leg information
                leg_info.append((tensor_id, leg_id, leg.operator))

    # Sort the leg information by tensor id and leg id
    sorted_leg_info = sorted(leg_info, key=lambda x: (x[0], x[1]))

    # Create the final output string
    output_string = ''.join(operator for _, _, operator in sorted_leg_info)

    return output_string


def collect_connected_leg_operators(tensor_list):
    # Initialize an empty string to store operator information
    connected_leg_operators = ""
    connected_leg_operators_string = ""

    # Iterate through all tensors
    for tensor in tensor_list:
        # Iterate through each leg of the tensor
        for leg in tensor.legs:
            if leg.connection is not None:
                target_tensor_index, target_leg_index = leg.connection
                for target in tensor_list:
                    if target.tensor_id == target_tensor_index:
                        target_tensor = target
                        target_leg = target_tensor.legs[target_leg_index]
                        connected_leg_operators += f"Tensor {tensor.tensor_id}, Leg " \
                                                   f"{tensor.legs.index(leg)}: {leg.operator} " \
                                                   f"-> Tensor {target_tensor.tensor_id}," \
                                                   f" Leg {target_tensor.legs.index(target_leg)}:" \
                                                   f" {target_leg.operator}\n"
                        connected_leg_operators_string += f"{leg.operator}"
    # Return the summarized operator information string
    return connected_leg_operators, connected_leg_operators_string


def traverse_h_gate(tensor_list):
    for tensor in tensor_list:
        for leg in tensor.legs:
            if (not leg.logical) and (leg.connection is not None):
                leg.clifford_gate = 'H'


def unblock_children_legs(tensor_list, tensor_id, logger_mode=False):
    # Iterate through tensors in tensor_list that are related to the given tensor_id
    if logger_mode:
        logger.info(f"\nUnblocking tensor {tensor_id}")
    current_tensor = get_tensor_from_id(tensor_list, tensor_id)
    # Iterate through all legs of this tensor
    for leg_index, leg in enumerate(current_tensor.legs):
        if leg.blocked and leg.connection is not None:
            # Get information about the connected target tensor
            target_tensor_id, target_leg_index = leg.connection
            target_tensor = get_tensor_from_id(tensor_list, target_tensor_id)
            if target_tensor.layer > current_tensor.layer:
                # If the connected target tensor is not in the specified list, unblock it
                leg.blocked = False
                # Also, unblock the leg on the connected target tensor
                target_leg = target_tensor.legs[target_leg_index]
                target_leg.blocked = False


def get_tensor_from_id(tensor_list, given_tensor_id):
    found_tensor = None
    for tensor in tensor_list:
        if tensor.tensor_id == given_tensor_id:
            found_tensor = tensor
            break
    return found_tensor


def write_layer(tensor_list, tensor_id_list, layer_num):
    for tensor_id in tensor_id_list:
        current_tensor = get_tensor_from_id(tensor_list, tensor_id)
        current_tensor.layer = layer_num


def connect_tensors(tensor_list, tensor_id1, tensor_id2):
    # Find the tensors with the given IDs
    tensor1 = get_tensor_from_id(tensor_list, tensor_id1)
    tensor2 = get_tensor_from_id(tensor_list, tensor_id2)

    # Create tensor if tensor does not exist
    if tensor1 is None:
        tensor1 = Tensor(tensor_id1, 0)
        tensor_list.append(tensor1)

    if tensor2 is None:
        tensor2 = Tensor(tensor_id2, 0)
        tensor_list.append(tensor2)

    # Check if the tensors are already connected
    for leg1 in tensor1.legs:
        if leg1.connection and leg1.connection[0] == tensor_id2:
            return  # Tensors are already connected

    # Create a new leg for each tensor and connect them
    leg1 = TensorLeg('I', (tensor_id2, len(tensor2.legs)))
    leg2 = TensorLeg('I', (tensor_id1, len(tensor1.legs)))

    tensor1.add_leg(leg1)
    tensor2.add_leg(leg2)


def swap_tensor_legs(tensor, leg_index_1, leg_index_2, tensor_list):
    # Step 1: Check if leg indexes are valid
    if leg_index_1 >= len(tensor.legs) or leg_index_2 >= len(tensor.legs):
        raise IndexError("Leg index is out of range.")

    # Step 2: Get the connection information on both sides of each leg
    connected_tensor_id_1 = None
    connected_tensor_id_2 = None
    connected_leg_index_1 = None
    connected_leg_index_2 = None
    if tensor.legs[leg_index_1].connection is not None:
        connected_tensor_id_1, connected_leg_index_1 = tensor.legs[leg_index_1].connection
    if tensor.legs[leg_index_2].connection is not None:
        connected_tensor_id_2, connected_leg_index_2 = tensor.legs[leg_index_2].connection

    # Step 3: Swap the operators on the legs
    tensor.legs[leg_index_1], tensor.legs[leg_index_2] = tensor.legs[leg_index_2], tensor.legs[leg_index_1]

    # Update the connection info in the tensors connected to these legs
    if connected_tensor_id_1 is not None:
        connected_tensor_1 = get_tensor_from_id(tensor_list, connected_tensor_id_1)
        connected_tensor_1_leg = connected_tensor_1.legs[connected_leg_index_1]
        connected_tensor_1_leg.connection = tensor.tensor_id, leg_index_2
    if connected_tensor_id_2 is not None:
        connected_tensor_2 = get_tensor_from_id(tensor_list, connected_tensor_id_2)
        connected_tensor_2_leg = connected_tensor_2.legs[connected_leg_index_2]
        connected_tensor_2_leg.connection = tensor.tensor_id, leg_index_1

# Example usage:
# swap_tensor_legs(tensor_to_modify, 0, 1, tensor_list)


def has_logical(tensor):
    """
    Check if any leg of the given tensor has the attribute 'logical' set to True.

    Args:
    tensor (Tensor): The tensor to check.

    Returns:
    bool: True if any leg of the tensor has 'logical' set to True, False otherwise.
    """
    for leg in tensor.legs:
        if leg.logical:  # If the 'logical' attribute of the leg is True
            return True
    return False
