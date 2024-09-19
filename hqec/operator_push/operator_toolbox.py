import numpy as np
from gurobipy import GRB, Model, or_


def pauli_product(operator_list):
    product = "I"
    for i in range(len(operator_list)):
        product = pairwise_pauli_product(product, operator_list[i])
    return product


def pairwise_pauli_product(operator1, operator2):
    if (operator1 not in ["I", "X", "Y", "Z"]) or (operator2 not in ["I", "X", "Y", "Z"]):
        print("None Pauli Operator Error")
        return
    product_table = [["I", "X", "Y", "Z"], ["X", "I", "Z", "Y"], ["Y", "Z", "I", "X"], ["Z", "Y", "X", "I"]]
    # Convert Operator1 and Operator2 into indices and get output
    operator_to_index = ["I", "X", "Y", "Z"]
    product = product_table[operator_to_index.index(operator1)][operator_to_index.index(operator2)]
    return product


def elementwise_product(list1, list2):
    # Check if the length of the input list is consistent
    if len(list1) != len(list2):
        return None  # Inconsistent lengths, unable to element-wise multiply

    # Create an empty list to store the results
    result = []

    # Define the multiplication rule for Pauli operators
    product_table = {
        ("I", "I"): "I",
        ("I", "X"): "X",
        ("I", "Y"): "Y",
        ("I", "Z"): "Z",
        ("X", "I"): "X",
        ("X", "X"): "I",
        ("X", "Y"): "Z",
        ("X", "Z"): "Y",
        ("Y", "I"): "Y",
        ("Y", "X"): "Z",
        ("Y", "Y"): "I",
        ("Y", "Z"): "X",
        ("Z", "I"): "Z",
        ("Z", "X"): "Y",
        ("Z", "Y"): "X",
        ("Z", "Z"): "I",
    }

    # Multiply element-wise and add the result to the result list
    for op1, op2 in zip(list1, list2):
        result.append(product_table[(op1, op2)])

    return result


def pauli_flip(operator):
    if operator == "X":
        return "Z"
    if operator == "Z":
        return "X"
    return operator


def multiply_ups(ups_list, power_list):
    # Check if the length of the input ups is consistent
    if len(set(len(ups) for ups in ups_list)) != 1:
        print("ups lengths are not consistent.")
        return None

    # Get the length of ups
    ups_length = len(ups_list[0])

    # Initialize the result as a list of all 'I'
    result = ["I"] * ups_length

    # Process each ups and its corresponding exponent.
    for ups, power in zip(ups_list, power_list):
        # If the exponent is 0 or 1, calculate the product when the power is 1.
        if power == 1:
            result = elementwise_product(result, ups)

    return result


def traverse_ups_powers(ups_list):
    # Calculate the length of the ups list.
    ups_length = len(ups_list)

    # Calculate the total possible power values.
    total_possibilities = 2**ups_length

    results = []  # Initialize an empty list to store the results.
    power_lists = []

    # Iterate through each possible power value.
    for power in range(total_possibilities):
        power_list = [int(bit) for bit in format(power, f"0{ups_length}b")]
        result = multiply_ups(ups_list, power_list)
        results.append(result)  # Append the result to the list.
        power_lists.append(power_list)

    return power_lists, results  # Return the list of results.


def count_non_i_operator_num(result_string):
    x = "X"
    y = "Y"
    z = "Z"
    n_x = result_string.count(x)
    n_y = result_string.count(y)
    n_z = result_string.count(z)
    n = n_x + n_y + n_z
    return n


def count_i_operator_num(result_string):
    i = "I"
    n_i = result_string.count(i)
    return n_i


def find_minimum_weight_representation_legacy(original_ups, stabilizer_generators):
    minimum_weight_ups = original_ups
    lowest_weight = count_non_i_operator_num(minimum_weight_ups)
    power_list, whole_stabilizer_group = traverse_ups_powers(stabilizer_generators)
    for stabilizer in whole_stabilizer_group:
        current_ups = elementwise_product(stabilizer, original_ups)
        current_weight = count_non_i_operator_num(current_ups)
        if current_weight < lowest_weight:
            lowest_weight = current_weight
            minimum_weight_ups = current_ups
    return minimum_weight_ups


# The legacy one is too expensive for mem


def find_minimum_weight_representation(original_ups, stabilizer_generators):
    # Convert str to list
    original_ups = ups_str_to_list(original_ups)
    for i, stabilizer_generator in enumerate(stabilizer_generators):
        stabilizer_generators[i] = ups_str_to_list(stabilizer_generator)
    minimum_weight_ups = original_ups
    lowest_weight = count_non_i_operator_num(minimum_weight_ups)
    selected_power = 0

    # Calculate the length of the stabilizer generators
    ups_length = len(stabilizer_generators)

    # Calculate the total possible power values.
    total_possibilities = 2**ups_length

    # Iterate through each possible power value.
    for power in range(total_possibilities):
        power_list = [int(bit) for bit in format(power, f"0{ups_length}b")]
        current_stabilizer = multiply_ups(stabilizer_generators, power_list)
        current_ups = elementwise_product(current_stabilizer, original_ups)
        current_weight = count_non_i_operator_num(current_ups)
        if current_weight < lowest_weight:
            lowest_weight = current_weight
            minimum_weight_ups = current_ups
            selected_power = power
            print(
                "lowest_weight: ",
                lowest_weight,
                "power: ",
                power_list,
                "\ncurrent_stabilizer",
                current_stabilizer,
                "\ncurrent_ups: ",
                current_ups,
            )
    return minimum_weight_ups, lowest_weight, selected_power


def find_approximate_minimum_weight_representation(original_ups, stabilizer_generators, k=100000):
    # Initialize with the original ups and its weight
    minimum_weight_ups = original_ups
    lowest_weight = count_non_i_operator_num(minimum_weight_ups)
    best_power_list = None

    # Calculate the length of the stabilizer generators
    ups_length = len(stabilizer_generators)

    # Perform k random samplings
    for _ in range(k):
        # Generate a random power_list
        power_list = np.random.randint(2, size=ups_length)

        # Calculate the current stabilizer and ups
        current_stabilizer = multiply_ups(stabilizer_generators, power_list)
        current_ups = elementwise_product(current_stabilizer, original_ups)
        current_weight = count_non_i_operator_num(current_ups)

        # If the current weight is lower, update the minimum weight and ups
        if current_weight < lowest_weight:
            lowest_weight = current_weight
            minimum_weight_ups = current_ups
            best_power_list = power_list

    return minimum_weight_ups, lowest_weight, best_power_list


# Example usage:
# approx_ups, approx_weight, approx_power_list = find_approximate_minimum_weight_representation(
#     original_ups, stabilizer_generators, k=1000
# )


def bit_distance(interested_tensor_id, pushed_results):
    # Check if interested_tensor_id points to a valid tensor
    if interested_tensor_id not in pushed_results:
        return

    # Get interested tensor's logical operators from pushed_results
    interested_tensors_logical_operators = []
    for interested_tensor_ups_result in pushed_results[interested_tensor_id].values():
        print(interested_tensor_ups_result)
        if interested_tensor_ups_result["logical"]:
            interested_tensors_logical_operators.append(interested_tensor_ups_result["result"])
    print("len of interested_tensors_logical_operators: ", len(interested_tensors_logical_operators))

    # Create stabilizer_generator_list_of_all_tensor
    stabilizer_generator_list_of_all_tensor = []
    for tensor_id in pushed_results:
        tensor_result = pushed_results[tensor_id]
        for tensor_ups_result in tensor_result.values():
            if not tensor_ups_result["logical"]:
                stabilizer_generator_list_of_all_tensor.append(tensor_ups_result["result"])
    print("len of stabilizer_generator_list_of_all_tensor: ", len(stabilizer_generator_list_of_all_tensor))

    # Evaluate distance for each logical operations of interested tensor
    minimum_weight_ups_list = []
    distances = []
    selected_powers = []
    for interested_tensors_logical_operator in interested_tensors_logical_operators:
        minimum_weight_ups, lowest_weight, selected_power = find_minimum_weight_representation(
            interested_tensors_logical_operator, stabilizer_generator_list_of_all_tensor
        )
        minimum_weight_ups_list.append(minimum_weight_ups)
        distances.append(lowest_weight)
        selected_powers.append(selected_power)
    print("minimum_weight_ups_list: ", minimum_weight_ups_list)
    print("distances: ", distances)
    print("selected_powers: ", selected_powers)


def ups_str_to_list(ups_str):
    ups_list = [single_pauli for single_pauli in ups_str]
    return ups_list


def bit_distance_by_layer(interested_tensor_id, pushed_results, tensor_list):
    if interested_tensor_id not in pushed_results:
        return

    interested_tensors_logical_operators = [
        result["result"] for result in pushed_results[interested_tensor_id].values() if result["logical"]
    ]

    # Create a dictionary to hold stabilizer generators by layer
    stabilizer_generators_by_layer = {}

    # Populate the dictionary with stabilizer generators, grouped by layer
    for tensor in tensor_list:
        layer = tensor.layer
        tensor_id = tensor.tensor_id
        if tensor_id in pushed_results:
            for result in pushed_results[tensor_id].values():
                if not result["logical"]:
                    stabilizer_generators_by_layer.setdefault(layer, []).append(result["result"])

    # Sort the dictionary by layer so we can process in order
    sorted_layers = sorted(stabilizer_generators_by_layer.keys())

    # Initialize the best results list
    best_results_per_layer = []

    for logical_id, logical_operator in enumerate(interested_tensors_logical_operators):
        best_weight = count_non_i_operator_num(logical_operator)
        best_ups = logical_operator
        best_power = None
        # Process each layer
        for layer in sorted_layers:
            stabilizer_generators = stabilizer_generators_by_layer[layer]
            print("layer", layer, "stabilizer_generators", stabilizer_generators)

            # Compute distance using generators of this layer
            ups, weight, power = find_approximate_minimum_weight_representation(best_ups, stabilizer_generators)

            if weight < best_weight:
                best_weight = weight
                best_ups = ups
                best_power = power

            # result for this layer, save it
            best_results_per_layer.append(
                {
                    "logical operator": logical_id,
                    "layer": layer,
                    "weight": best_weight,
                    "ups": best_ups,
                    "power": best_power,
                }
            )

    # Output the best results per layer
    for result in best_results_per_layer:
        print(
            f"logical operator {result['logical operator']} \nLayer {result['layer']}: "
            f"Weight {result['weight']}, UPS {result['ups']}, "
            f"Power {result['power']}"
        )


# Example usage:
# bit_distance(interested_tensor_id, pushed_results, tensor_list)


def minimize_operator_weight(
    op, stabilizers, punish_index_list=None, punishment=1, time_limit=None, mip_focus=0, heuristics=0, output_flag=0
):
    # Create model
    model = Model("minimize_logical_operator_weight")

    model.setParam("NodefileStart", 32)  # GB

    model.setParam("OutputFlag", output_flag)

    # Set parameters
    if time_limit is not None:
        model.setParam(GRB.Param.TimeLimit, time_limit)

    model.setParam(GRB.Param.MIPFocus, mip_focus)

    model.setParam(GRB.Param.Heuristics, heuristics)

    half_l = int(len(op) / 2)

    # Define variables
    z = model.addVars(len(op), vtype=GRB.BINARY, name="z")
    u = model.addVars(len(op), vtype=GRB.INTEGER, name="u")  # Ancilla variable
    v = model.addVars(half_l, vtype=GRB.BINARY, name="v")

    # Create a binary variable λ, corresponding to whether to use each stabilizer.
    lambda_vars = model.addVars(len(stabilizers), vtype=GRB.BINARY, name="lambda")

    # Add constraints to the new logical operations for each element, ensuring modulo-2 arithmetic.
    for i in range(len(op)):
        # Calculate the weighted sum of stabilizers.
        stabilizer_sum = sum(stabilizers[j][i] * lambda_vars[j] for j in range(len(stabilizers)))
        # Add linear constraints for modulo-2 arithmetic.
        model.addConstr(z[i] + 2 * u[i] == stabilizer_sum + op[i])

    for i in range(half_l):
        model.addConstr(v[i] == or_(z[i], z[i + half_l]))
        # model.addConstr(v[i] == z[i] + z[i + half_l])

    # Set the objective function to minimize Hamming weight.
    print("HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH", punish_index_list)
    if punish_index_list:
        print("PPPPPPPPPPPPPPPPP")
        model.setObjective(
            sum(punishment * v[i] for i in range(half_l) if i in punish_index_list)
            + sum(v[i] for i in range(half_l) if i not in punish_index_list),
            GRB.MINIMIZE,
        )
    else:
        model.setObjective(sum(v[i] for i in range(half_l)), GRB.MINIMIZE)

    # Solve the model.
    model.optimize()

    # Print the results.
    if bool(output_flag):
        for var in lambda_vars.values():
            print(f"{var.varName} = {var.x}")
        print(f"Weight (wt) of the new logical operator: {model.objVal}")
        if model.status == GRB.OPTIMAL:
            print("OPTIMAL")
        else:
            print("No optimal solution found")

    # Return lambda values
    lambda_values = [var.x for var in lambda_vars.values()]
    return lambda_values


def apply_mod2_sum(op, stabilizers, lambda_values):
    # Convert stabilizers_and_logical to a NumPy array if it's not already
    stabilizers_and_logical_np = np.array(stabilizers)

    # Initialize the result vector, initially the same as e
    result = op.copy()

    # Iterate through each stabilizer and its corresponding lambda value
    for lambda_val, stabilizer in zip(lambda_values, stabilizers_and_logical_np):
        if lambda_val:  # If lambda value is 1, apply modulo 2 addition
            result = np.bitwise_xor(result, stabilizer)

    return result
