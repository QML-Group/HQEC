import os
import tempfile

from decoder_pauli import calculate_pauli_weight, minimize_error_operator_weight
from hqec.input_processor import (
    collect_logical_xs,
    collect_logical_zs,
    collect_stabilizers,
    process_quantum_csv,
)
from hqec.operator_processor import (
    apply_mod2_sum,
    batch_convert_to_binary_vectors,
    binary_vector_to_pauli,
    pauli_to_binary_vector,
)


file_path = os.path.join(tempfile.gettempdir(), "distance_vs_n", "happy_zero", "happy", "r_3", "output.csv")
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
lambda_results = minimize_error_operator_weight(L, rrr, mip_focus=3, heuristics=0.2)
binary_result = apply_mod2_sum(L, rrr, lambda_results)
print(binary_result)
result = binary_vector_to_pauli(binary_result)
print(result)
min_wt = calculate_pauli_weight(result)
print(f"min_wt: {min_wt}")
