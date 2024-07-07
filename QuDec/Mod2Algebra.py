import numpy as np
import itertools


def mod2_matrix_multiply(a, b):
    # Perform regular matrix multiplication.
    c = a @ b
    # Apply modulo 2 operation.
    c_mod2 = c % 2
    return c_mod2


def mod2_matrix_vector_multiply(A, x):
    """
    Perform matrix-vector multiplication in modulo 2 arithmetic.

    Args:
    A (np.array): The matrix.
    x (np.array): The vector.

    Returns:
    np.array: The result of the matrix-vector multiplication in modulo 2 arithmetic.
    """
    # Perform regular matrix-vector multiplication
    result = np.dot(A, x)

    # Apply modulo 2 operation
    result_mod2 = result % 2
    return result_mod2


def mod2_gaussian_elimination(matrix):
    rows, cols = matrix.shape
    pivot_row = 0

    for col in range(cols):
        # Find the pivot element in the current column.
        pivot = None
        for row in range(pivot_row, rows):
            if matrix[row, col] == 1:
                pivot = row
                break

        # If the pivot element is found, perform row swapping and elimination.
        if pivot is not None:
            # Move the row containing the pivot element to the top.
            matrix[[pivot_row, pivot]] = matrix[[pivot, pivot_row]]

            # Eliminate other non-zero elements in the current column using XOR operation.
            for row in range(rows):
                if row != pivot_row and matrix[row, col] == 1:
                    matrix[row] ^= matrix[pivot_row]

            pivot_row += 1

    return matrix


def mod2_inverse(a):
    rows, cols = a.shape
    if rows != cols:
        raise ValueError("The matrix must be square.")

    # Create the augmented matrix [A | I].
    identity = np.eye(rows, dtype=np.int32)
    a_identity = np.concatenate((a, identity), axis=1)

    # Apply modulo 2 Gaussian elimination.
    a_identity_rref = mod2_gaussian_elimination(a_identity)

    # Check if the left side is the identity matrix to ensure A is invertible.
    if not np.array_equal(a_identity_rref[:, :cols], np.eye(rows, dtype=np.int32)):
        raise ValueError("The matrix is not invertible.")

    # Extract the right-hand matrix, which is the inverse of A.
    return a_identity_rref[:, cols:]


def find_kj(vectors, j):
    # Ensure a valid index is provided
    if j >= len(vectors):
        raise ValueError("Index j is out of the range of vectors.")

    # Add all vectors except S_j
    sum_vector = np.sum(np.array([v for i, v in enumerate(vectors) if i != j]), axis=0)

    # Get vj
    vj = sum_vector

    # Find the positions of zero elements in Vj
    zero_positions = np.where(vj == 0)[0]

    # Find corresponding non-zero positions in Sj
    sj = vectors[j]
    for pos in zero_positions:
        if sj[pos] == 1:
            # Construct Kj
            kj = np.zeros_like(sj)
            kj[pos] = 1
            return kj

    # If no suitable position is found, return a failure message
    return None


def mod2_right_inverse(a):
    rows, cols = a.shape
    b = np.zeros((cols, rows), dtype=np.int32)  # Initialize matrix B

    # For each row of A
    for j in range(rows):
        kj = find_kj(a, j)
        if kj is not None:
            b[:, j] = kj  # Set the found Kj as a column of B

    return b


def sort_rref_matrix_by_pivots(matrix):
    """
    Sort the rows of a matrix in RREF format based on the position of the leading elements (pivots).

    Args:
    matrix (np.array): The matrix in RREF format.

    Returns:
    np.array: The sorted matrix.
    """
    # Identify the pivot positions
    pivot_positions = [np.argmax(row) if np.any(row) else -1 for row in matrix]

    # Sort the rows based on the pivot positions
    sorted_matrix = sorted(matrix, key=lambda row: np.argmax(row) if np.any(row) else np.inf)

    return np.array(sorted_matrix)


def solve_homogeneous_system_max_ones(A, sj_binary_filtered):
    rows, cols = A.shape
    x = [None] * cols

    for i in range(rows - 1, -1, -1):
        row = A[i]
        ones_indices = np.where(row == 1)[0]
        num_ones = len(ones_indices)

        if num_ones == 0:
            continue

        if num_ones % 2 == 0:  # Even number of 1s
            if all(x[idx] != 0 for idx in ones_indices):  # Cases 1.2 and 1.3
                if any(x[idx] is None for idx in ones_indices):
                    for idx in ones_indices:
                        if x[idx] is None:
                            x[idx] = 1
            else:  # Cases 1.1 and 1.4
                for idx in ones_indices:
                    x[idx] = 1

        else:  # Odd number of 1s
            pivot = ones_indices[0]  # Position of the pivot element
            if all(x[idx] is None for idx in ones_indices):  # Case 2.1
                x[pivot] = 0
                for idx in ones_indices[1:]:
                    x[idx] = 1
            elif any(x[idx] is None for idx in ones_indices):  # Cases 2.2 and 2.3
                x[pivot] = 0
                for idx in ones_indices:
                    if x[idx] is None:
                        x[idx] = 1
        temp_x = [0 if v is None else v for v in x]
        product = mod2_matrix_multiply(np.array(sj_binary_filtered), np.array(temp_x))
        print("temp_x", temp_x, "product", product)

    # Set the remaining None values to 0
    x = [0 if v is None else v for v in x]
    return x


def adjust_x_to_anticommute_with_sj(A, x, filtered_sj, max_attempts_per_change=100):
    common_ones_indices = [i for i, (x_val, sj_val) in enumerate(zip(x, filtered_sj)) if x_val == 1 and sj_val == 1]
    num_common_ones = len(common_ones_indices)

    for num_changes in range(1, num_common_ones + 1, 2):  # Consider only odd number of changes
        attempt_count = 0
        for indices_to_change in itertools.combinations(common_ones_indices, num_changes):
            if attempt_count >= max_attempts_per_change:
                break  # Reached the maximum number of attempts

            trial_x = x.copy()
            for idx in indices_to_change:
                trial_x[idx] = 0
            print(indices_to_change)
            while True:
                for row_idx, row in enumerate(A):
                    if np.dot(row, trial_x) % 2 == 1:
                        conflict_indices = [i for i, val in enumerate(row) if val == 1 and trial_x[i] == 1]
                        if conflict_indices:
                            trial_x[conflict_indices[0]] = 0
                            break
                else:
                    if any(trial_x):
                        if np.dot(trial_x, filtered_sj) % 2 == 1:
                            return trial_x
                    break

            attempt_count += 1

    return None


def solve_homogeneous_system_max_ones_with_anti_commutativity(A, filtered_sj, max_attempts_per_change=1000):
    x = solve_homogeneous_system_max_ones(A, filtered_sj)
    if np.dot(x, filtered_sj) % 2 == 1:
        return x

    adjusted_x = adjust_x_to_anticommute_with_sj(A, x, filtered_sj, max_attempts_per_change)
    return adjusted_x if adjusted_x is not None else x

# Example usage
# A = ...  # Define the matrix A
# filtered_sj = ...  # Define filtered sj
# x = solve_homogeneous_system_max_ones_with_anti_commutativity(A, filtered_sj, max_attempts_per_change=100)
# print(x)  # Output the adjusted x


def find_kj_that_anticommutes_with_jth_row_only(A, j, zero_column_indices):
    """
    Find a binary vector kj that anticommmutes with only the jth row of matrix A and commutes with all other rows,
    with the additional constraint that kj must have zeros at the specified indices.

    Args:
    A (np.array): A binary matrix representing the si vectors.
    j (int): The row index with which kj should anticommute.
    zero_column_indices (list): Indices where kj must have zero elements.

    Returns:
    list or None: The binary vector kj if found, otherwise None.
    """
    rows, cols = A.shape
    for potential_kj in itertools.product([0, 1], repeat=cols):
        if any(potential_kj[idx] != 0 for idx in zero_column_indices):  # Check if kj has zeros at specified indices
            continue

        anticommuting_with_j = commute_product(A[j], potential_kj) == 1
        commuting_with_others = all(commute_product(A[i], potential_kj) == 0 for i in range(rows) if i != j)

        if anticommuting_with_j and commuting_with_others:
            return list(potential_kj)

    return None

# Example usage
# A = ...  # Define the matrix A
# j = ...  # Define the row index j
# zero_column_indices = ...  # Define the indices where kj must have zeros
# kj = find_kj_that_anticommutes_with_jth_row_only(A, j, zero_column_indices)
# print(kj)  # Output the found kj or None


def find_k_that_anticommutes_with_jth_rows(A, j_list, zero_column_indices):
    """
    Find a binary vector kj that anticommmutes with only the jth row of matrix A and commutes with all other rows,
    with the additional constraint that kj must have zeros at the specified indices.

    Args:
    A (np.array): A binary matrix representing the si vectors.
    j_list (list of int): The row indices with which k should anticommute.
    zero_column_indices (list): Indices where k must have zero elements.

    Returns:
    list or None: The binary vector k if found, otherwise None.
    """
    rows, cols = A.shape
    for potential_k in itertools.product([0, 1], repeat=cols):
        if any(potential_k[idx] != 0 for idx in zero_column_indices):  # Check if kj has zeros at specified indices
            continue

        anticommuting_with_j_list = all(commute_product(A[j], potential_k) == 1 for j in j_list)
        commuting_with_others = all(commute_product(A[i], potential_k) == 0 for i in range(rows) if i not in j_list)

        if anticommuting_with_j_list and commuting_with_others:
            return list(potential_k)

    return None


def find_zero_columns_in_stabilizers(stabilizer_list):
    """
    Find the indices of columns that are all zeros in a binary formatted stabilizer matrix.

    Args:
    stabilizer_list (list of list): A list of binary formatted stabilizers.

    Returns:
    list: A list of indices of columns that are all zeros.
    """
    # Convert the list of stabilizers into a numpy array
    stabilizer_matrix = np.array(stabilizer_list)
    zero_column_indices = []

    # Iterate over columns and check if all elements are zero
    for col_idx in range(stabilizer_matrix.shape[1]):
        if np.all(stabilizer_matrix[:, col_idx] == 0):
            zero_column_indices.append(col_idx)

    return zero_column_indices


def find_zero_columns_in_pairs(stabilizer_list):
    """
    Find pairs of indices (k, k+n) of columns that are all zeros in a binary formatted stabilizer matrix,
    where the total number of columns is 2n and 0 < k <= n.

    Args:
    stabilizer_list (list of list): A list of binary formatted stabilizers.

    Returns:
    list: A list of tuples, where each tuple contains the indices (k, k+n) of columns that are all zeros.
    """
    # Convert the list of stabilizers into a numpy array
    stabilizer_matrix = np.array(stabilizer_list)
    zero_column_pairs = []

    # Number of columns should be even, get n
    n = stabilizer_matrix.shape[1] // 2

    # Iterate over the first n columns and check if both the kth and (k+n)th columns are all zeros
    for col_idx in range(n):
        if np.all(stabilizer_matrix[:, col_idx] == 0) and np.all(stabilizer_matrix[:, col_idx + n] == 0):
            zero_column_pairs.append(col_idx)
            zero_column_pairs.append(col_idx + n)

    return zero_column_pairs


def commute_product(a, b):
    half_n = len(a) // 2  # Calculate n/2

    a_x = a[:half_n]
    a_z = a[half_n:]

    b_x = b[:half_n]
    b_z = b[half_n:]

    product = (np.dot(a_x, b_z) + np.dot(b_x, a_z)) % 2

    return product


def swap_and_mod2_multiply(A, B):
    """
    Swap the left and right halves of a matrix A with an even number of columns,
    then perform a mod 2 matrix multiplication with another matrix B.

    Parameters:
    A (numpy.ndarray): An even-columned matrix to be swapped and multiplied.
    B (numpy.ndarray): The matrix to multiply with A_swap.

    Returns:
    numpy.ndarray: The result of mod 2 matrix multiplication of A_swap and B.
    """

    # Validate that A has an even number of columns
    if A.shape[1] % 2 != 0:
        raise ValueError("Matrix A must have an even number of columns")

    # Split A into two halves and swap them
    middle_index = A.shape[1] // 2
    left_half, right_half = A[:, :middle_index], A[:, middle_index:]
    A_swap = np.hstack((right_half, left_half))

    # Perform matrix multiplication and then mod 2
    result = np.dot(A_swap, B) % 2

    return result
