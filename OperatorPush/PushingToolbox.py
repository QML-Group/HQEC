import logging
import copy
from OperatorPush.TensorToolbox import read_out_boundary, read_out_logical, collect_connected_leg_operators, \
    unblock_children_legs, write_layer, get_tensor_from_id
import csv
import multiprocessing

# Config logging
logging.basicConfig(filename='OperatorPush.log', level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Create a logger
logger = logging.getLogger('OperatorPush')


def auto_operator_push_decision(tensor_list, start_tensor_id, logger_mode=False):
    # Create a set to keep track of tensors that have been processed
    processed_tensors = set()
    tensors_for_next_round = []

    # Initialize the queue with the start_tensor_id
    queue = [start_tensor_id]
    tensors_for_current_round = queue[:]

    # Initialize the layer info
    layer = 0

    # Iterate while there are tensors in the queue
    while queue:
        # Get the tensor ID to process in this round
        tensor_id = queue.pop(0)

        # Check if the tensor has already been processed
        if tensor_id in processed_tensors:
            continue

        # Get the tensor based on its ID
        current_tensor = None
        for target in tensor_list:
            if target.tensor_id == tensor_id:
                current_tensor = target
                break

        # Execute operator_push_decision on the current tensor
        tensor_for_ups_reconsider = current_tensor.operator_push_decision(tensor_list, tensors_for_current_round,
                                                                          logger_mode=logger_mode)

        if tensor_for_ups_reconsider is not None:
            if len(tensor_for_ups_reconsider) != 0:
                if tensor_for_ups_reconsider[0] in processed_tensors:
                    queue.insert(0, tensor_for_ups_reconsider[0])
                    processed_tensors.remove(tensor_for_ups_reconsider[0])
                    unblock_children_legs(tensor_list, tensor_for_ups_reconsider[0], logger_mode=logger_mode)

        # Add the current tensor to the set of processed tensors
        processed_tensors.add(tensor_id)

        # Find neighbors of the current tensor
        for neighbor in current_tensor.get_connections():
            if neighbor not in processed_tensors:
                if neighbor not in tensors_for_next_round:
                    if neighbor not in tensors_for_current_round:
                        tensors_for_next_round.append(neighbor)

        # Add unprocessed neighbors to the queue if queue is empty (current round is over)
        if len(queue) == 0:
            # Write layer info to tensors
            write_layer(tensor_list, tensors_for_current_round, layer)
            layer += 1

            queue = tensors_for_next_round[:]
            tensors_for_current_round = tensors_for_next_round[:]
            tensors_for_next_round = []


def push_operator(tensor_list, ups, tensor_id, logger_mode=False):
    # Apply ups on the chosen tensor
    chosen_tensor = get_tensor_from_id(tensor_list, tensor_id)
    chosen_tensor.apply_operators_to_legs(ups)

    # Mark the chosen tensor as the starting tensor
    chosen_tensor.starting_tensor = True

    # Print information for each tensor, including leg connection details
    if logger_mode:
        logger.info(f"Starting from tensor {tensor_id}, aiming to push operator: {ups}")
        logger.info('Tensors before pushing')
        for tensor in tensor_list:
            logger.info(f"Tensor {tensor.tensor_id}:")
            logger.info(tensor)

    # Do pushing
    auto_operator_push_decision(tensor_list, 0, logger_mode=logger_mode)

    # Print information for each tensor, including leg connection details
    if logger_mode:
        logger.info('Tensors after pushing')
        for tensor in tensor_list:
            logger.info(f"Tensor {tensor.tensor_id}:")
            logger.info(tensor)

    internal, internal_string = collect_connected_leg_operators(tensor_list)
    if 'X' in internal_string or 'Z' in internal_string or 'Y' in internal_string:
        raise ValueError("Non I internal leg")
    result = read_out_boundary(tensor_list, logger_mode=logger_mode)
    logical = read_out_logical(tensor_list)
    if logger_mode:
        logger.info("\nStart reading out boundary operators")
        logger.info(f'Result: {str(result)}')
        logger.info(f'Logical: {str(logical)}')

    return str(result)


def batch_push(tensor_list, logger_mode=False):
    results = {}  # Dictionary for storing the return values

    # Iterate through each tensor
    for tensor in tensor_list:
        tensor_id = tensor.tensor_id
        # For each tensor, push stabilizer, logical Z, and logical X operators separately
        stabilizers_results = {}
        logical_z_results = {}
        logical_x_results = {}
        for index, ups in enumerate(tensor.stabilizer_list):
            temp_tensor_list = copy.deepcopy(tensor_list)
            result = push_operator(temp_tensor_list, ups, tensor_id, logger_mode=logger_mode)
            stabilizers_results['stabilizer' + str(index + 1)] = result

        for index, ups in enumerate(tensor.logical_z_list):
            temp_tensor_list = copy.deepcopy(tensor_list)
            result = push_operator(temp_tensor_list, ups, tensor_id, logger_mode=logger_mode)
            logical_z_results['logical_z' + str(index + 1)] = result

        for index, ups in enumerate(tensor.logical_x_list):
            temp_tensor_list = copy.deepcopy(tensor_list)
            result = push_operator(temp_tensor_list, ups, tensor_id, logger_mode=logger_mode)
            logical_x_results['logical_x' + str(index + 1)] = result

        # Save all results for the current tensor
        results[tensor_id] = {
            'stabilizers': stabilizers_results,
            'logical_z': logical_z_results,
            'logical_x': logical_x_results
        }

    # Write to a CSV file
    with open('output.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)

        # Write the results for each tensor
        for tensor_id, tensor_results in results.items():
            row = [str(tensor_id)]
            # Add stabilizers results
            for key, value in tensor_results['stabilizers'].items():
                row.append(f"{key} = {value}")
            # Add logical Z results
            for key, value in tensor_results['logical_z'].items():
                row.append(f"{key} = {value}")
            # Add logical X results
            for key, value in tensor_results['logical_x'].items():
                row.append(f"{key} = {value}")
            writer.writerow(row)

    return results  # Return a dictionary containing the results

# Example usage:
# results = batch_push(tensor_list)


def process_tensor(tensor, tensor_list, logger_mode):
    tensor_id = tensor.tensor_id
    results = {}
    stabilizers_results = {}
    logical_z_results = {}
    logical_x_results = {}

    for index, ups in enumerate(tensor.stabilizer_list):
        temp_tensor_list = copy.deepcopy(tensor_list)
        result = push_operator(temp_tensor_list, ups, tensor_id, logger_mode=logger_mode)
        stabilizers_results['stabilizer' + str(index + 1)] = result

    for index, ups in enumerate(tensor.logical_z_list):
        temp_tensor_list = copy.deepcopy(tensor_list)
        result = push_operator(temp_tensor_list, ups, tensor_id, logger_mode=logger_mode)
        logical_z_results['logical_z' + str(index + 1)] = result

    for index, ups in enumerate(tensor.logical_x_list):
        temp_tensor_list = copy.deepcopy(tensor_list)
        result = push_operator(temp_tensor_list, ups, tensor_id, logger_mode=logger_mode)
        logical_x_results['logical_x' + str(index + 1)] = result

    results[tensor_id] = {
        'stabilizers': stabilizers_results,
        'logical_z': logical_z_results,
        'logical_x': logical_x_results
    }

    return results


def batch_push_multiprocessing(tensor_list, logger_mode=False):
    results = {}  # Dictionary for storing the return values

    # Create a pool of workers equal to the number of available CPU cores
    pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())

    # Launch the process_tensor function for each tensor in parallel
    process_results = [pool.apply_async(process_tensor, args=(tensor, tensor_list, logger_mode)) for tensor in tensor_list]

    # Close the pool and wait for each task to complete
    pool.close()
    pool.join()

    # Collect results from each process
    for result in process_results:
        results.update(result.get())

    # Write to a CSV file
    with open('output.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for tensor_id, tensor_results in results.items():
            row = [str(tensor_id)]
            for key, value in tensor_results['stabilizers'].items():
                row.append(f"{key} = {value}")
            for key, value in tensor_results['logical_z'].items():
                row.append(f"{key} = {value}")
            for key, value in tensor_results['logical_x'].items():
                row.append(f"{key} = {value}")
            writer.writerow(row)

    return results  # Return a dictionary containing the results

# Example usage:
# results = batch_push(tensor_list)
