from OperatorPush.Presets.Zero_Rate_HaPPY_new_for_kj import setup_zero_rate_happy
from OperatorPush.PushingToolbox import batch_push
from QuDec.InputProcessor import extract_stabilizers_from_result_dict, extract_logicals_from_result_dict
from DIstanceFind.OperatorProcessor import pauli_to_binary_vector, batch_convert_to_binary_vectors, apply_mod2_sum, \
    binary_vector_to_pauli
from DIstanceFind.DistanceFInder import minimize_logical_operator_weight, calculate_pauli_weight

if __name__ == '__main__':
    tensor_list = setup_zero_rate_happy(R=1)
    results_dict = batch_push(tensor_list)
    stabilizers = extract_stabilizers_from_result_dict(results_dict)
    logical_zs, logical_xs = extract_logicals_from_result_dict(results_dict)
    bi_stabilizers = batch_convert_to_binary_vectors(stabilizers)
    bi_log_z = pauli_to_binary_vector(logical_zs[0])
    lambda_results = minimize_logical_operator_weight(bi_log_z, bi_stabilizers, mip_focus=3, heuristics=0)
    print(f"lambda_results: {lambda_results}")
    binary_min_wt_log_z = apply_mod2_sum(bi_log_z, bi_stabilizers, lambda_results)
    min_wt_log_z = binary_vector_to_pauli(binary_min_wt_log_z)
    print(f"min_wt_log_z: {min_wt_log_z}")
    min_wt = calculate_pauli_weight(min_wt_log_z)
    print(f"min_wt: {min_wt}")
