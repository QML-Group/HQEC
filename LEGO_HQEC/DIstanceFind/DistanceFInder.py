from gurobipy import GRB, Model, or_


def minimize_logical_operator_weight(L, stabilizers, time_limit=None, mip_focus=3, heuristics=0):
    # Create model
    model = Model("minimize_logical_operator_weight")

    model.setParam('NodefileStart', 32)  # GB

    # model.setParam('Presolve', 2)
    #
    # model.setParam('Cuts', 3)

    # Set parameters
    if time_limit is not None:
        model.setParam(GRB.Param.TimeLimit, time_limit)

    model.setParam(GRB.Param.MIPFocus, mip_focus)

    model.setParam(GRB.Param.Heuristics, heuristics)

    half_l = int(len(L) / 2)

    # Define variables
    z = model.addVars(len(L), vtype=GRB.BINARY, name="z")
    u = model.addVars(len(L), vtype=GRB.INTEGER, name="u")  # Ancilla variable
    v = model.addVars(half_l, vtype=GRB.BINARY, name="v")

    # Create a binary variable λ, corresponding to whether to use each stabilizer.
    lambda_vars = model.addVars(len(stabilizers), vtype=GRB.BINARY, name="lambda")

    # Add constraints to the new logical operations for each element, ensuring modulo-2 arithmetic.
    for i in range(len(L)):
        # Calculate the weighted sum of stabilizers.
        stabilizer_sum = sum(
            stabilizers[j][i] * lambda_vars[j] for j in range(len(stabilizers)))
        # Add linear constraints for modulo-2 arithmetic.
        model.addConstr(z[i] + 2 * u[i] == stabilizer_sum + L[i])

    for i in range(half_l):
        model.addConstr(v[i] == or_(z[i], z[i + half_l]))

    # Set the objective function to minimize Hamming weight.
    model.setObjective(sum(v[i] for i in range(half_l)), GRB.MINIMIZE)

    # Solve the model.
    model.optimize()

    # Return lambda values
    lambda_values = [var.x for var in lambda_vars.values()]
    return lambda_values

# Example usage
# L = [1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0]
# stabilizers = [
#     [1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0],
#     [0, 1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0],
#     [1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0],
#     [0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0]
# ]
# minimize_logical_operator_weight(L, stabilizers)


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
