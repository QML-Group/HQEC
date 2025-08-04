def pauli_to_binary_vector(pauli_string):
    """
    Convert a Pauli operator string to a binary vector.

    Args:
    pauli_string (str): A string of Pauli operators (I, X, Z, Y).

    Returns:
    list: A binary vector representing the presence of X and Z operators.
    """
    length = len(pauli_string)
    binary_vector = [0] * (2 * length)

    for i, char in enumerate(pauli_string):
        if char in ['X', 'Y']:
            binary_vector[i] = 1  # X or Y present, set corresponding X part
        if char in ['Z', 'Y']:
            binary_vector[length + i] = 1  # Z or Y present, set corresponding Z part

    return binary_vector

# Example usage
# pauli_string = 'IIXXZYXI'
# binary_vector = pauli_to_binary_vector(pauli_string)
# print(binary_vector)


def batch_convert_to_binary_vectors(stabilizers):
    """
    Convert a list of Pauli operator strings (stabilizers) to a list of binary vectors.

    Args:
    stabilizers (list): A list of Pauli operator strings.

    Returns:
    list: A list of binary vectors corresponding to the Pauli operator strings.
    """
    return [pauli_to_binary_vector(stabilizer) for stabilizer in stabilizers]

# Example usage
# Assuming stabilizers is the list obtained from the collect_stabilizers function
# binary_vectors = batch_convert_to_binary_vectors(stabilizers)
# print(binary_vectors)


def apply_mod2_sum(L, stabilizers, lambda_values):
    # Initialize the result vector, initially the same as L
    result = L.copy()

    # Iterate through each stabilizer and its corresponding lambda value
    for lambda_val, stabilizer in zip(lambda_values, stabilizers):
        if lambda_val:  # If lambda value is 1, apply modulo 2 addition
            result = [r ^ s for r, s in zip(result, stabilizer)]

    return result

# Example usage
# L = [1, 1, 0, 0, 1]
# stabilizers = [
#     [1, 0, 1, 0, 1],
#     [0, 1, 0, 1, 0],
#     [1, 1, 1, 1, 1]
# ]
# lambda_values = [1, 0, 1]  # Assume these are the lambda values you computed earlier
# result = apply_mod2_sum(L, stabilizers, lambda_values)
# print("Result:", result)


def binary_vector_to_pauli(binary_vector):
    """
    Convert a binary vector back to a Pauli operator string.

    Args:
    binary_vector (list): A binary vector representing the presence of X and Z operators.

    Returns:
    str: A string of Pauli operators (I, X, Z, Y).
    """
    length = len(binary_vector) // 2
    pauli_string = ""

    for i in range(length):
        if binary_vector[i] == 0 and binary_vector[length + i] == 0:
            pauli_string += 'I'
        elif binary_vector[i] == 1 and binary_vector[length + i] == 0:
            pauli_string += 'X'
        elif binary_vector[i] == 0 and binary_vector[length + i] == 1:
            pauli_string += 'Z'
        elif binary_vector[i] == 1 and binary_vector[length + i] == 1:
            pauli_string += 'Y'

    return pauli_string

# Example usage
# binary_vector = [0, 0, 1, 1, 1, 0, 0, 1, 0, 0, 1, 1, 1, 0, 1, 0]
# pauli_string = binary_vector_to_pauli(binary_vector)
# print(pauli_string)
