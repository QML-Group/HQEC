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


def gf2_matrix_inverse(A):
    """
    Compute the inverse of a square matrix over GF(2) using Gauss–Jordan elimination.
    A must be shape (n, n). Raises if singular.
    """
    A = GF2(A)
    n, m = A.shape
    assert n == m, "Only square matrices can be inverted."

    # Build augmented matrix [A | I]
    I = GF2.Identity(n)
    aug = np.concatenate([A, I], axis=1)  # shape (n, 2n), FieldArray

    aug = aug.copy()  # ensure it's mutable

    # Gauss–Jordan elimination over GF(2)
    row = 0
    for col in range(n):
        # Find a pivot row with aug[r, col] == 1
        pivot = None
        for r in range(row, n):
            if aug[r, col] == 1:
                pivot = r
                break
        if pivot is None:
            raise np.linalg.LinAlgError("Matrix is not invertible over GF(2) (no pivot in a column).")
        # Swap pivot row to the current row
        if pivot != row:
            aug[[pivot, row], :] = aug[[row, pivot], :]
        # Zero out the column in all other rows (XOR in GF(2))
        for r in range(n):
            if r != row and aug[r, col] == 1:
                aug[r, :] ^= aug[row, :]
        row += 1
        if row == n:
            break

    # Left block is now I; right block is A^{-1}
    A_inv = aug[:, n:]
    return A_inv


def gf2_left_inverse_fast(A):
    """
    Construct a left inverse over GF(2).
    A: (m, n), requires full column rank (rank = n, m >= n).
    Returns L: (n, m) such that L @ A = I_n.
    Single pass row-reduction recording row ops (R ∈ GF(2)^{m×m}); take the top n rows of R.
    Complexity ~ O(m * n^2); no combinatorial search or matrix inversion.
    """
    A = GF2(A)                 # (m, n)
    m, n = A.shape
    R = GF2.Identity(m)        # Accumulates row operations

    row = 0
    for col in range(n):
        # 1) Find a pivot row with A[row:, col] == 1
        pivot = None
        for r in range(row, m):
            if A[r, col] == 1:
                pivot = r
                break
        if pivot is None:
            # No pivot in this column → not full column rank
            continue

        # 2) Swap pivot row to current 'row'
        if pivot != row:
            A[[row, pivot], :] = A[[pivot, row], :]
            R[[row, pivot], :] = R[[pivot, row], :]

        # 3) Eliminate this column in all other rows (XOR in GF(2))
        for r in range(m):
            if r != row and A[r, col] == 1:
                A[r, :] ^= A[row, :]
                R[r, :] ^= R[row, :]

        row += 1
        if row == n:
            break

    if row < n:
        raise np.linalg.LinAlgError("A has insufficient column rank over GF(2) (rank < n); cannot construct a left inverse.")

    # Now R @ (original A) = [I_n; 0]. The top n rows of R form the left inverse.
    L = R[:n, :]               # (n, m)
    return L

