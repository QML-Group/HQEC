import numpy as np
import galois


GF2 = galois.GF(2)

def mod2_matrix_multiply(a, b):
    # Perform regular matrix multiplication.
    c = a @ b
    # Apply modulo 2 operation.
    c_mod2 = c % 2
    return c_mod2


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


def gf2_pinv(matrix):
    matrix_gf2 = GF2(matrix)
    m, n = matrix_gf2.shape
    r = np.linalg.matrix_rank(matrix_gf2)

    if r < min(m, n):
        raise np.linalg.LinAlgError(
            "Matrix is singular and cannot be inverted."
        )

    if r == n:
        return np.linalg.inv(matrix_gf2.T @ matrix_gf2) @ matrix_gf2.T

    else:
        return matrix_gf2.T @ np.linalg.inv(matrix_gf2 @ matrix_gf2.T)
