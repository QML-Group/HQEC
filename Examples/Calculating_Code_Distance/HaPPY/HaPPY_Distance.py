from OperatorPush.Presets.Zero_Rate_HaPPY_new_for_kj import setup_zero_rate_happy
from OperatorPush.PushingToolbox import batch_push, batch_push_multiprocessing
from QuDec.InputProcessor import extract_stabilizers_from_result_dict, extract_logicals_from_result_dict
from DIstanceFind.OperatorProcessor import pauli_to_binary_vector, batch_convert_to_binary_vectors, apply_mod2_sum, \
    binary_vector_to_pauli
from DIstanceFind.DistanceFInder import minimize_logical_operator_weight, calculate_pauli_weight

if __name__ == '__main__':
    # Initialize parameters
    R = 0  # Radius

    # Set up the HaPPY code tensor network
    tensor_list = setup_zero_rate_happy(R=R)

    # Perform parallel operator pushing operations on the tensor network
    results_dict = batch_push_multiprocessing(tensor_list)

    # Extract stabilizers and logical operators from the results (in string form)
    stabilizers = extract_stabilizers_from_result_dict(results_dict)
    logical_zs, logical_xs = extract_logicals_from_result_dict(results_dict)

    # Convert stabilizers to binary/symplectic representation
    symplectic_stabilizers = batch_convert_to_binary_vectors(stabilizers)

    # Convert the first Z-type logical operator to binary vector (to calculate the distance of this operator)
    L = pauli_to_binary_vector(logical_zs[0])

    # Find the minimal weight equivalent logical operator by solving a MIP problem
    lambda_results = minimize_logical_operator_weight(L=L, stabilizers=symplectic_stabilizers,
                                                      mip_focus=3, heuristics=0.2)

    # Apply the found coefficients to get the minimal weight operator in binary form
    binary_result = apply_mod2_sum(L=L, stabilizers=symplectic_stabilizers,
                                   lambda_values=lambda_results)

    # Convert the binary result back to Pauli operator form
    result = binary_vector_to_pauli(binary_result)

    # Calculate and print the weight (number of non-identity terms) of the minimal operator
    min_wt = calculate_pauli_weight(result)
    print(f"Distance of the chosen operator = {min_wt}")  # This is the distance for the Z logical operator
