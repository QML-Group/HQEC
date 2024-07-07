from DIstanceFind.InputProcessor import process_quantum_csv, collect_stabilizers, collect_logical_xs, collect_logical_zs, \
    read_tensor_layers_from_csv
from DIstanceFind.OperatorProcessor import pauli_to_binary_vector, batch_convert_to_binary_vectors, apply_mod2_sum, \
    binary_vector_to_pauli
from DIstanceFind.DistanceFInder import minimize_logical_operator_weight, calculate_pauli_weight

file_path = "A:\范峻瑜\大学这会儿\【3.0】TU Delft\【2.1】 Y2 Q1\Master Thesis\Distance_VS_n\HaPPY Zero\HaPPY\R=3\output.csv"
res = process_quantum_csv(file_path)
stabilizers = collect_stabilizers(res)
logical_zs = collect_logical_zs(res)
logical_xs = collect_logical_xs(res)
qubit_logical_z = ''
qubit_logical_x = ''
tensor_operators = res[str(0)]
for op_type, op_value in tensor_operators.items():
    if 'logical_z' in op_type:
        qubit_logical_z = op_value
    if 'logical_x' in op_type:
        qubit_logical_x = op_value
oli = stabilizers
rrr = batch_convert_to_binary_vectors(oli)
L = pauli_to_binary_vector(qubit_logical_z)
print(L)
lambda_results = minimize_logical_operator_weight(L, rrr, mip_focus=3, heuristics=0.2)
binary_result = apply_mod2_sum(L, rrr, lambda_results)
print(binary_result)
result = binary_vector_to_pauli(binary_result)
print(result)
min_wt = calculate_pauli_weight(result)
print(f"min_wt: {min_wt}")
