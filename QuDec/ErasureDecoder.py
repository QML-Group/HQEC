import random
import numpy as np
from QuDec.OperatorProcessor import batch_convert_to_binary_vectors
from QuDec.Mod2Algebra import mod2_gaussian_elimination
from multiprocessing import Pool, current_process
import psutil


def filter_pauli_strings_by_erasure(pauli_strings, erasure_vector):
    """
    Filter Pauli operator strings based on an erasure error vector.

    Args:
    pauli_strings (list of str): List of Pauli operator strings.
    erasure_vector (list of int): Binary vector indicating erasure errors (1 for error, 0 for no error).

    Returns:
    list of str: List of filtered Pauli operator strings with characters removed at positions where erasure_vector is 0.
    """
    filtered_strings = []

    for string in pauli_strings:
        filtered_string = ""
        for i, char in enumerate(string):
            if erasure_vector[i] == 1:
                filtered_string += char
        filtered_strings.append(filtered_string)

    return filtered_strings

# Example usage
# pauli_strings = ['IXYZ', 'ZZXY', 'YXIZ']
# erasure_vector = [0, 1, 1, 0]  # Assuming erasure errors at positions 1 and 2
# filtered_pauli_strings = filter_pauli_strings_by_erasure(pauli_strings, erasure_vector)
# print(filtered_pauli_strings)


def generate_erasure_vector(p, n):
    """
    Generate an erasure vector of length n where each component has a probability p of being 1.

    Args:
    p (float): Probability of a single qubit error.
    n (int): Length of the erasure vector.

    Returns:
    list: Erasure vector of length n.
    """
    return [1 if random.random() < p else 0 for _ in range(n)]

# Example usage
# p = 0.2  # Example probability
# n = 10  # Example length
# erasure_vector = generate_erasure_vector(p, n)
# erasure_vector


def generate_fixed_weight_erasure_vector(k, n):
    """
    Generate an erasure vector of length n with exactly k erasures (1s).

    Args:
    k (int): Number of erasure errors (1s) in the vector.
    n (int): Length of the erasure vector.

    Returns:
    list: Erasure vector of length n with k erasures.
    """
    if k > n:
        raise ValueError("Number of erasures cannot be greater than the vector length.")

    # Create a list with k 1s and (n-k) 0s
    erasure_vector = [1]*k + [0]*(n-k)

    # Shuffle the list to randomize the positions of 1s and 0s
    random.shuffle(erasure_vector)

    return erasure_vector

# Example usage
# k = 3  # Number of erasures
# n = 10  # Length of vector
# erasure_vector = generate_fixed_weight_erasure_vector(k, n)
# print(erasure_vector)


def generate_complementary_vector(erasure_vector):
    """
    Generate a vector where each element is the complement (opposite) of the input erasure vector.

    Args:
    erasure_vector (list): The input erasure vector.

    Returns:
    list: The complementary vector.
    """
    return [1 - element for element in erasure_vector]


def can_recover_from_erasure(operator_list, erasure_vector, num_logical_operators):
    """
    Determine if the given erasure vector can be recovered using the provided stabilizers and logical operators.
    Recovery is possible unless there is a row in the RREF of the matrix, where the last 'num_logical_operators'
    elements contain a non-zero element, and all other elements are zero.

    Args:
    operator_list (list of str): List of Pauli operator strings representing stabilizers and logical operators.
    erasure_vector (list of int): Binary vector indicating erasure errors (1 for error, 0 for no error).
    num_logical_operators (int): Number of logical operators.

    Returns:
    bool: True if recovery is possible, False otherwise.
    """
    # Filter and convert Pauli strings to binary vectors
    filtered_pauli_strings = filter_pauli_strings_by_erasure(operator_list, erasure_vector)
    binary_vectors = batch_convert_to_binary_vectors(filtered_pauli_strings)
    binary_matrix = np.array(binary_vectors).T

    # Apply mod2 Gaussian elimination to get the matrix in RREF
    rref_matrix = mod2_gaussian_elimination(binary_matrix)

    # Check if there is a row indicating the system is unsolvable
    for row in rref_matrix:
        if np.all(row[:-num_logical_operators] == 0) and np.any(row[-num_logical_operators:] != 0):
            return False  # Found a row indicating no solution

    return True  # No such row found, recovery is possible


def calculate_recovery_rate_single_process(args):
    operator_list, erasure_vector, num_logical_operators, affinity = args
    # Set CPU affinity for the process if specified
    if affinity is not None:
        p = psutil.Process(current_process().pid)
        p.cpu_affinity(affinity)

    return can_recover_from_erasure(operator_list, erasure_vector, num_logical_operators)


def calculate_recovery_rate_multiprocessing(n, p, stabilizers, logical_operators, n_process=1, cpu_affinity_list=None):
    """
    Calculate the recovery rate from erasure errors for a given set of stabilizers and logical operators using
    multiprocessing.

    Args:
    n (int): Number of repetitions to generate random erasure vectors.
    p (float): Probability of a single qubit error.
    stabilizers (list of str): List of Pauli operator strings representing stabilizers.
    logical_operators (list of str): List of logical operator strings.
    n_process (int): Number of processes to use for multiprocessing.
    cpu_affinity_list (list): List of CPU cores to set affinity for each process.

    Returns:
    float: The recovery success rate.
    """
    operator_list = stabilizers + logical_operators
    num_logical_operators = len(logical_operators)

    # Generate erasure vectors for multiprocessing
    erasure_vectors = [generate_erasure_vector(p, len(operator_list[0])) for _ in range(n)]
    params = [(operator_list, vec, num_logical_operators, cpu_affinity_list) for i, vec in enumerate(erasure_vectors)]

    with Pool(n_process) as pool:
        results = pool.map(calculate_recovery_rate_single_process, params)

    successful_recoveries = sum(results)
    return successful_recoveries / n

# Example usage:
# n = 1000  # Number of repetitions
# p = 0.1  # Probability of a single qubit error
# stabilizers = ['IXYZ', 'ZZXY', ...]  # Example stabilizers
# logical_operators = ['XXXX', ...]  # Example logical operators
# n_process = 4  # Number of processes
# cpu_affinity_list = [0, 1, 2, 3]  # List of CPU cores for setting affinity
# success_rate = calculate_recovery_rate_multiprocessing(n, p, stabilizers, logical_operators, n_process, cpu_affinity_list)
# print(f"Decoding success rate: {success_rate}")


def calculate_recovery_rates_for_p_range(n, p_start, p_end, p_step, stabilizers, logical_operators,
                                         n_process=1, cpu_affinity_list=None):
    """
    Calculate the recovery rates for a range of erasure probabilities with multiple logical operators,
    optionally using multiprocessing for improved performance.

    Args:
    n (int): Number of repetitions to generate random erasure vectors.
    p_start (float): Starting probability of a single qubit error.
    p_end (float): Ending probability of a single qubit error.
    p_step (float): Step size for the probability range.
    stabilizers (list of str): List of Pauli operator strings representing stabilizers.
    logical_operators (list of str): List of logical operator strings.
    n_process (int): Number of processes to use for multiprocessing.
    cpu_affinity_list (list): List of CPU cores to set affinity for each process.

    Returns:
    list of tuples: Each tuple contains a probability value and its corresponding recovery success rate.
    """
    recovery_rates = []
    for p in np.arange(p_start, p_end + p_step, p_step):
        print(f"Running at p = {p}")
        recovery_rate = calculate_recovery_rate_multiprocessing(n=n, p=p, stabilizers=stabilizers,
                                                                logical_operators=logical_operators,
                                                                n_process=n_process,
                                                                cpu_affinity_list=cpu_affinity_list)
        recovery_rates.append((p, recovery_rate))

    return recovery_rates

# Example usage with multiprocessing:
# n = 1000  # Number of repetitions
# p_start = 0.1  # Starting probability
# p_end = 0.5  # Ending probability
# p_step = 0.05  # Probability step
# stabilizers = ['IXYZ', 'ZZXY', 'YXIZ']  # Example stabilizers
# logical_operators = ['XXXX', 'ZZZZ']  # Example logical operators
# n_process = 4  # Number of processes
# cpu_affinity_list = [0, 1, 2, 3]  # List of CPU cores for setting affinity (optional)
# rates = calculate_recovery_rates_for_p_range(n, p_start, p_end, p_step, stabilizers, logical_operators,
#                                              n_process, cpu_affinity_list)
# for rate in rates:
#     print(f"Probability: {rate[0]}, Recovery Rate: {rate[1]}")

