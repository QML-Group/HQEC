import numpy as np
from gurobipy import GRB, Model, or_


def pauli_product(operator_list):
    product = 'I'
    for i in range(len(operator_list)):
        product = pairwise_pauli_product(product, operator_list[i])
    return product


def pairwise_pauli_product(operator1, operator2):
    if (operator1 not in ['I', 'X', 'Y', 'Z']) or (operator2 not in ['I', 'X', 'Y', 'Z']):
        print("None Pauli Operator Error")
        return
    product_table = [['I', 'X', 'Y', 'Z'], ['X', 'I', 'Z', 'Y'], ['Y', 'Z', 'I', 'X'], ['Z', 'Y', 'X', 'I']]
    # Convert Operator1 and Operator2 into indices and get output
    operator_to_index = ['I', 'X', 'Y', 'Z']
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
        ('I', 'I'): 'I',
        ('I', 'X'): 'X',
        ('I', 'Y'): 'Y',
        ('I', 'Z'): 'Z',
        ('X', 'I'): 'X',
        ('X', 'X'): 'I',
        ('X', 'Y'): 'Z',
        ('X', 'Z'): 'Y',
        ('Y', 'I'): 'Y',
        ('Y', 'X'): 'Z',
        ('Y', 'Y'): 'I',
        ('Y', 'Z'): 'X',
        ('Z', 'I'): 'Z',
        ('Z', 'X'): 'Y',
        ('Z', 'Y'): 'X',
        ('Z', 'Z'): 'I',
    }

    # Multiply element-wise and add the result to the result list
    for op1, op2 in zip(list1, list2):
        result.append(product_table[(op1, op2)])

    return result


def pauli_flip(operator):
    if operator == 'X':
        return 'Z'
    if operator == 'Z':
        return 'X'
    return operator


def multiply_ups(ups_list, power_list):
    # Check if the length of the input ups is consistent
    if len(set(len(ups) for ups in ups_list)) != 1:
        print("ups lengths are not consistent.")
        return None

    # Get the length of ups
    ups_length = len(ups_list[0])

    # Initialize the result as a list of all 'I'
    result = ['I'] * ups_length

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
    total_possibilities = 2 ** ups_length

    results = []  # Initialize an empty list to store the results.
    power_lists = []

    # Iterate through each possible power value.
    for power in range(total_possibilities):
        power_list = [int(bit) for bit in format(power, f'0{ups_length}b')]
        result = multiply_ups(ups_list, power_list)
        results.append(result)  # Append the result to the list.
        power_lists.append(power_list)

    return power_lists, results  # Return the list of results.


def minimize_operator_weight(op, stabilizers, time_limit=None, mip_focus=0, heuristics=0, output_flag=0):
    # Create model
    model = Model("minimize_logical_operator_weight")

    model.setParam('OutputFlag', output_flag)

    model.setParam('NodefileStart', 32)  # GB

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
    model.setObjective(sum(v[i] for i in range(half_l)), GRB.MINIMIZE)

    # Solve the model.
    model.optimize()

    # Print the results.
    if bool(output_flag):
        for var in lambda_vars.values():
            print(f'{var.varName} = {var.x}')
        print(f'Weight (wt) of the new logical operator: {model.objVal}')
        if model.status == GRB.OPTIMAL:
            print("OPTIMAL")
        else:
            print('No optimal solution found')

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
