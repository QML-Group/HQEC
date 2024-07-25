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
