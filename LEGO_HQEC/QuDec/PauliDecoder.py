from gurobipy import GRB, Model, or_, and_
import random
from LEGO_HQEC.QuDec.Mod2Algebra import mod2_matrix_multiply, mod2_gaussian_elimination
from LEGO_HQEC.QuDec.OperatorProcessor import batch_convert_to_binary_vectors, binary_vector_to_pauli, apply_mod2_sum
from LEGO_HQEC.QuDec.Mod2Algebra import swap_and_mod2_multiply, gf2_pinv
import numpy as np
import os
import psutil
from multiprocessing import Process, Queue, Pool
import math


def minimize_error_operator_weight(e, stabilizers_and_logical, time_limit=None, mip_focus=0, heuristics=0,
                                   output_flag=0):
    # Create model
    model = Model("minimize_logical_operator_weight")

    model.setParam('OutputFlag', output_flag)

    model.setParam('NodefileStart', 32)  # GB

    # Set parameters
    if time_limit is not None:
        model.setParam(GRB.Param.TimeLimit, time_limit)

    model.setParam(GRB.Param.MIPFocus, mip_focus)

    model.setParam(GRB.Param.Heuristics, heuristics)

    half_l = int(len(e) / 2)

    # Define variables
    z = model.addVars(len(e), vtype=GRB.BINARY, name="z")
    u = model.addVars(len(e), vtype=GRB.INTEGER, name="u")  # Ancilla variable
    v = model.addVars(half_l, vtype=GRB.BINARY, name="v")

    # Create a binary variable λ, corresponding to whether to use each stabilizer.
    lambda_vars = model.addVars(len(stabilizers_and_logical), vtype=GRB.BINARY, name="lambda")

    # Add constraints to the new logical operations for each element, ensuring modulo-2 arithmetic.
    for i in range(len(e)):
        # Calculate the weighted sum of stabilizers.
        stabilizer_sum = sum(stabilizers_and_logical[j][i] * lambda_vars[j] for j in range(len(stabilizers_and_logical)))
        # Add linear constraints for modulo-2 arithmetic.
        model.addConstr(z[i] + 2 * u[i] == stabilizer_sum + e[i])

    for i in range(half_l):
        model.addConstr(v[i] == or_(z[i], z[i + half_l]))

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

# Example usage
# e = [1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0]
# stabilizers_and_logical = [
#     [1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0],
#     [0, 1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0],
#     [1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0],
#     [0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0]
# ]
# minimize_logical_operator_weight(L, stabilizers)


def minimize_error_operator_weight_y2(e, stabilizers_and_logical, time_limit=None, mip_focus=0, heuristics=0,
                                   output_flag=0):
    # Create model
    model = Model("minimize_logical_operator_weight")

    model.setParam('OutputFlag', output_flag)

    model.setParam('NodefileStart', 32)  # GB

    # Set parameters
    if time_limit is not None:
        model.setParam(GRB.Param.TimeLimit, time_limit)

    model.setParam(GRB.Param.MIPFocus, mip_focus)

    model.setParam(GRB.Param.Heuristics, heuristics)

    # Define variables
    z = model.addVars(len(e), vtype=GRB.BINARY, name="z")
    u = model.addVars(len(e), vtype=GRB.INTEGER, name="u")  # Ancilla variable

    # Create a binary variable λ, corresponding to whether to use each stabilizer.
    lambda_vars = model.addVars(len(stabilizers_and_logical), vtype=GRB.BINARY, name="lambda")

    # Add constraints to the new logical operations for each element, ensuring modulo-2 arithmetic.
    for i in range(len(e)):
        # Calculate the weighted sum of stabilizers.
        stabilizer_sum = sum(stabilizers_and_logical[j][i] * lambda_vars[j] for j in range(len(stabilizers_and_logical)))
        # Add linear constraints for modulo-2 arithmetic.
        model.addConstr(z[i] + 2 * u[i] == stabilizer_sum + e[i])

    # Set the objective function to minimize Hamming weight.
    model.setObjective(sum(z[i] for i in range(len(e))), GRB.MINIMIZE)

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

# Example usage
# e = [1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0]
# stabilizers_and_logical = [
#     [1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0],
#     [0, 1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0],
#     [1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0],
#     [0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0]
# ]
# minimize_logical_operator_weight(L, stabilizers)


def minimize_error_operator_weight_optimal(e, stabilizers_and_logical, a, b, c, time_limit=None, mip_focus=0,
                                           heuristics=0, output_flag=0):
    # Create model
    model = Model("minimize_logical_operator_weight_optimal")

    model.setParam('OutputFlag', output_flag)

    model.setParam('NodefileStart', 32)  # GB

    # Set parameters
    if time_limit is not None:
        model.setParam(GRB.Param.TimeLimit, time_limit)

    model.setParam(GRB.Param.MIPFocus, mip_focus)

    model.setParam(GRB.Param.Heuristics, heuristics)

    half_l = int(len(e) / 2)

    # Define variables
    z = model.addVars(len(e), vtype=GRB.BINARY, name="z")
    u = model.addVars(len(e), vtype=GRB.INTEGER, name="u")  # Ancilla variable
    v = model.addVars(half_l, vtype=GRB.BINARY, name="v")

    # Create a binary variable λ, corresponding to whether to use each stabilizer.
    lambda_vars = model.addVars(len(stabilizers_and_logical), vtype=GRB.BINARY, name="lambda")

    # Add constraints to the new logical operations for each element, ensuring modulo-2 arithmetic.
    for i in range(len(e)):
        # Calculate the weighted sum of stabilizers.
        stabilizer_sum = sum(stabilizers_and_logical[j][i] * lambda_vars[j] for j in range(len(stabilizers_and_logical)))
        # Add linear constraints for modulo-2 arithmetic.
        model.addConstr(z[i] + 2 * u[i] == stabilizer_sum + e[i])

    for i in range(half_l):
        model.addConstr(v[i] == and_(z[i], z[i + half_l]))

    # Set the objective function to minimize Hamming weight.
    model.setObjective(sum(a*z[i] + c*v[i] + b*z[i+half_l] for i in range(half_l)), GRB.MINIMIZE)

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

# Example usage
# e = [1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0]
# stabilizers_and_logical = [
#     [1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0],
#     [0, 1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0],
#     [1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0],
#     [0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0]
# ]
# minimize_logical_operator_weight(L, stabilizers)


def generate_pauli_error_vector(px, py, pz, n):
    """
    Generate a Pauli error vector based on the probabilities of X, Y, Z errors for qubits.

    Args:
    px (float): Probability of an X error.
    py (float): Probability of a Y error.
    pz (float): Probability of a Z error.
    n (int): Number of qubits.

    Returns:
    list: A binary vector representing the presence of X and Z errors.
    """
    error_vector = [0] * (2 * n)

    for i in range(n):
        # Generate a random number to determine the error type
        rand_num = random.random()
        if rand_num < px:
            error_vector[i] = 1  # X error
        elif rand_num < px + py:
            error_vector[i] = 1  # Y error
            error_vector[n + i] = 1
        elif rand_num < px + py + pz:
            error_vector[n + i] = 1  # Z error

    return error_vector


def calculate_syndrome(stabilizer_matrix, pauli_error_vector):
    """
    Calculate the syndrome vector from a given stabilizer matrix and a Pauli error vector.

    Args:
    stabilizer_matrix (np.array): The stabilizer matrix.
    pauli_error_vector (list): The Pauli error vector.

    Returns:
    np.array: The syndrome vector.
    """
    # Convert the Pauli error vector to a numpy array
    error_vector_np = np.array(pauli_error_vector)

    # Calculate the syndrome vector
    syndrome_vector = swap_and_mod2_multiply(stabilizer_matrix, error_vector_np)
    return syndrome_vector

# Example usage
# stabilizer_matrix = np.array([
#     [1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0],
#     [0, 1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0],
#     [1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0],
#     [0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0]
# ])
# pauli_error_vector = [1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0]
# syndrome_vector = calculate_syndrome(stabilizer_matrix, pauli_error_vector)
# print(syndrome_vector)


def decoding_process(queue, px, py, pz, stabilizers, stabilizer_matrix, stabilizers_and_logical, f, n, time_limit,
                     mip_focus, heuristics, output_flag):
    try:
        # Generate a random Pauli error vector
        e_0 = generate_pauli_error_vector(px, py, pz, n)
        # print(f"e0: {e_0}, type {type(e_0)}")
        # print(stabilizers_and_logical)

        # Calculate the syndrome vector
        y = calculate_syndrome(stabilizer_matrix, e_0)

        # Estimate the error using the pseudo-inverse matrix
        e = mod2_matrix_multiply(f, y)
        # print(f"e: {e}, type {type(e)}")

        # Try to minimize the weight of the error operator
        lambda_values = minimize_error_operator_weight(list(e), stabilizers_and_logical,
                                                       time_limit=time_limit, mip_focus=mip_focus,
                                                       heuristics=heuristics, output_flag=output_flag)

        lambda_values_int = np.round(lambda_values).astype(int)

        # Apply the lambda values to get the minimal weight error
        e_bar = apply_mod2_sum(e, stabilizers_and_logical, lambda_values_int)

        # Compare the estimated error with the actual error
        is_successful = is_error_equivalent(stabilizers, e_0, e_bar)
        queue.put(is_successful)

    except Exception as e:
        print(f"Error encountered in iteration, error: {e}. Retrying...")
        queue.put(False)


def decoding_iteration(px, py, pz, stabilizers_and_other_logs, stabilizer_matrix, stabilizers_and_logical, f, n,
                       time_limit, mip_focus, heuristics, output_flag, affinity=None, pass_all_info=False):
    try:
        # Set CPU affinity for the process if specified
        if affinity is not None:
            p = psutil.Process(os.getpid())
            p.cpu_affinity(affinity)

        # Generate a random Pauli error vector
        e_0 = generate_pauli_error_vector(px, py, pz, n)

        # Calculate the syndrome vector
        y = calculate_syndrome(stabilizer_matrix, e_0)

        # Estimate the error using the pseudo-inverse matrix
        e = mod2_matrix_multiply(f, y)

        if pass_all_info:
            # print(f'px{px}, py{py}, pz{pz}')
            p_ele = (px + py + pz) / 3
            if px < 0:
                px = 0
            if py < 0:
                py = 0
            if pz < 0:
                pz = 0
            wtx = math.log(px+1e-300, p_ele)
            wty = math.log(py+1e-300, p_ele)
            wtz = math.log(pz+1e-300, p_ele)
            a = wtx
            b = wtz
            c = wty - a - b
            # Minimize the weight of the error operator
            lambda_values = minimize_error_operator_weight_optimal(list(e), stabilizers_and_logical, a=a, b=b, c=c,
                                                                   time_limit=time_limit, mip_focus=mip_focus,
                                                                   heuristics=heuristics, output_flag=output_flag)
        else:
            # Minimize the weight of the error operator
            lambda_values = minimize_error_operator_weight(list(e), stabilizers_and_logical,
                                                           time_limit=time_limit, mip_focus=mip_focus,
                                                           heuristics=heuristics, output_flag=output_flag)

        lambda_values_int = np.round(lambda_values).astype(int)

        # Apply the lambda values to get the minimal weight error
        e_bar = apply_mod2_sum(e, stabilizers_and_logical, lambda_values_int)

        # Compare the estimated error with the actual error
        return is_error_equivalent(stabilizers_and_other_logs, e_0, e_bar)

    except Exception as e:
        print(f"Error in decoding iteration: {e}")
        return False


def quantum_error_correction_decoder_multiprocess(tensor_list, stabilizers, logical_xs, logical_zs, logical_x,
                                                  logical_z, px, py, pz, N, n_process, cpu_affinity_list=None,
                                                  time_limit=None, mip_focus=0, heuristics=0, output_flag=0, f=None,
                                                  pass_all_info=False):
    stabilizers_binary = batch_convert_to_binary_vectors(stabilizers)
    logical_xs_binary = batch_convert_to_binary_vectors(logical_xs)
    logical_zs_binary = batch_convert_to_binary_vectors(logical_zs)
    stabilizers_and_logical = stabilizers_binary + logical_xs_binary + logical_zs_binary
    stabilizer_matrix = np.array(stabilizers_binary)
    if f is None:
        f = create_f(symplectic_stabilizers=stabilizers_binary)
    n = len(stabilizers[0])
    print(f"px, py, pz: {px, py, pz}")
    stabilizers_and_other_logs = stabilizers + logical_xs + logical_zs
    stabilizers_and_other_logs.remove(logical_x)
    stabilizers_and_other_logs.remove(logical_z)

    args = [(px, py, pz, stabilizers_and_other_logs, stabilizer_matrix, stabilizers_and_logical, f, n, time_limit,
             mip_focus, heuristics, output_flag, cpu_affinity_list, pass_all_info) for _ in range(N)]

    successful_decodings = 0
    with Pool(n_process) as pool:
        results = pool.starmap(decoding_iteration, args)
        successful_decodings = sum(results)

    success_rate = successful_decodings / N
    return success_rate


# 使用方法
# success_rate = quantum_error_correction_decoder_multiprocess(tensor_list, stabilizers, logical_xs, logical_zs, px, py, pz, N, n_process)
# print(f"Decoding success rate: {success_rate}")


def quantum_error_correction_decoder(tensor_list, stabilizers, logical_xs, logical_zs, px, py, pz, N,
                                     time_limit=None, mip_focus=0, heuristics=0, output_flag=0):
    # Convert stabilizers and logical operators to binary vectors
    stabilizers_binary = batch_convert_to_binary_vectors(stabilizers)
    logical_xs_binary = batch_convert_to_binary_vectors(logical_xs)
    logical_zs_binary = batch_convert_to_binary_vectors(logical_zs)
    stabilizers_and_logical = stabilizers_binary + logical_xs_binary + logical_zs_binary

    # Convert to numpy matrix
    stabilizer_matrix = np.array(stabilizers_binary)

    # Calculate the pseudo-inverse matrix F
    f = create_f(symplectic_stabilizers=stabilizers_binary)

    # Get the length of stabilizers (number of qubits)
    n = len(stabilizers[0])

    successful_decodings = 0

    for _ in range(N):
        while True:  # 使用循环来允许重试
            queue = Queue()
            p = Process(target=decoding_process, args=(
                queue, px, py, pz, stabilizers, stabilizer_matrix, stabilizers_and_logical, f, n, time_limit,
                mip_focus, heuristics, output_flag))
            p.start()
            p.join()

            if p.exitcode != 0:
                # 检测到子进程异常终止
                print(f"Severe error encountered in subprocess, retrying iteration {_}")
                continue  # 重试当前迭代

            result = queue.get()
            if result:
                successful_decodings += 1
                print(f"px: {px}, py: {py}, pz: {pz}, round {_}, succ")
            else:
                print(f"px: {px}, py: {py}, pz: {pz}, round {_}, fail")
            break  # 正常完成，跳出循环进入下一次迭代

    # Calculate and return the decoding success rate
    success_rate = successful_decodings / N
    return success_rate

# Example usage
# Define your stabilizers, logical_xs, logical_zs
# stabilizers = ['IXYZ', 'ZZXY', ...]
# logical_xs = ['XXXX', ...]
# logical_zs = ['ZZZZ', ...]
# px, py, pz = 0.1, 0.05, 0.15
# N = 1000
# success_rate = quantum_error_correction_decoder(stabilizers, logical_xs, logical_zs, px, py, pz, N)
# print(f"Decoding success rate: {success_rate}")


def is_error_equivalent(stabilizers, e_0, e_bar):
    e_combine = (np.array(e_0) + np.array(e_bar)) % 2
    string_e_combine = binary_vector_to_pauli(e_combine)
    augmented_list = stabilizers + [string_e_combine]
    augmented_vectors = batch_convert_to_binary_vectors(augmented_list)
    binary_augmented_matrix = np.array(augmented_vectors).T

    # Apply mod2 Gaussian elimination to get the matrix in RREF
    rref_matrix = mod2_gaussian_elimination(binary_augmented_matrix)
    np.set_printoptions(threshold=np.inf)
    # print(rref_matrix)

    # Check if there is a row indicating the system is unsolvable
    for row in rref_matrix:
        if np.all(row[:-1] == 0) and np.any(row[-1:] != 0):
            return False  # Found a row indicating no solution

    return True  # No such row found, recovery is possible


def calculate_pauli_weight(pauli_string):
    """
    Calculate the weight of a Pauli operator string.

    Args:
    pauli_string (str): A string of Pauli operators (I, X, Z, Y).

    Returns:
    int: The weight of the Pauli string (number of non-I operators).
    """
    weight = 0
    for char in pauli_string:
        if char != 'I':
            weight += 1
    return weight

# Example
# pauli_string = 'IIXXZYXI'
# weight = calculate_pauli_weight(pauli_string)
# print(weight)


def filter_pauli_operator_list(A, B):
    """
    Filter a list of Pauli operator strings based on the non-I elements of a given Pauli operator string.

    Args:
    A (str): A Pauli operator string used as a filter.
    B (list of str): A list of Pauli operator strings to be filtered.

    Returns:
    list of str: The filtered list of Pauli operator strings.
    """
    filtered_B = []
    for pauli_string in B:
        filtered_string = ''.join(pauli_char for a_char, pauli_char in zip(A, pauli_string) if a_char != 'I')
        filtered_B.append(filtered_string)

    return filtered_B

# Example usage
# A = 'IXZI'
# B = ['XXXX', 'ZZZZ', 'YYYY', 'ZZII']
# filtered_B = filter_pauli_operator_list(A, B)
# print(filtered_B)  # ['XX', 'ZZ', 'YY']


def create_f(symplectic_stabilizers):
    if not isinstance(symplectic_stabilizers, list) or not symplectic_stabilizers:
        raise ValueError("Input must be a non-empty list.")

    for row in symplectic_stabilizers:
        if not isinstance(row, list):
            raise ValueError("Each row must be a list.")

    n = int(len(symplectic_stabilizers[0])/2)

    identity_matrix = np.eye(n, dtype=int)
    zeros_block = np.zeros((n, n), dtype=int)
    lambda_matrix = np.block([[zeros_block, identity_matrix], [identity_matrix, zeros_block]])
    s_lambda_matrix = lambda_matrix @ np.array(symplectic_stabilizers).T
    f = gf2_pinv(s_lambda_matrix).T.tolist()

    return f
