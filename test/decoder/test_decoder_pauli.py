import os

import pytest

from hqec.decoder.decoder_pauli import minimize_error_operator_weight
from hqec.decoder.pauli import calculate_pauli_weight
from hqec.input_processor import (
    collect_logical_xs,
    collect_logical_zs,
    collect_stabilizers,
    process_quantum_csv,
    read_tensor_layers_from_csv,
)
from hqec.operator_processor import (
    apply_mod2_sum,
    batch_convert_to_binary_vectors,
    binary_vector_to_pauli,
    pauli_to_binary_vector,
)


def test_happy_zero__r_3():
    current_dir = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(current_dir, "happy_zero__r_3.csv")
    res = process_quantum_csv(file_path)
    stabilizers = collect_stabilizers(res)
    logical_zs = collect_logical_zs(res)
    logical_xs = collect_logical_xs(res)
    qubit_logical_z = ""
    qubit_logical_x = ""
    tensor_operators = res[str(0)]
    for op_type, op_value in tensor_operators.items():
        if "logical_z" in op_type:
            qubit_logical_z = op_value
        if "logical_x" in op_type:
            qubit_logical_x = op_value
    oli = stabilizers
    rrr = batch_convert_to_binary_vectors(oli)
    L = pauli_to_binary_vector(qubit_logical_z)
    assert L == ""
    lambda_results = minimize_error_operator_weight(L, rrr, mip_focus=3, heuristics=0.2)
    binary_result = apply_mod2_sum(L, rrr, lambda_results)
    assert binary_result == ""
    result = binary_vector_to_pauli(binary_result)
    assert result == ""
    min_wt = calculate_pauli_weight(result)
    assert min_wt == ""


def test_htn_vertex_res__l_5():
    current_dir = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(current_dir, "htn_vertex_res__l_5.csv")
    layer_file_path = os.path.join(current_dir, "htn_vertex_res__l_5__tensor_layers.csv")
    tensor_layers = read_tensor_layers_from_csv(layer_file_path)
    res = process_quantum_csv(file_path)
    stabilizers = collect_stabilizers(res)
    logical_zs = collect_logical_zs(res)
    logical_xs = collect_logical_xs(res)
    qubit_logical_z = ""
    qubit_logical_x = ""
    oli = stabilizers
    for tensor_id in tensor_layers:
        tensor_layer = tensor_layers[tensor_id]
        tensor_operators = res[str(tensor_id)]
        if tensor_layer == 0:
            for op_type, op_value in tensor_operators.items():
                if "logical_z" in op_type:
                    qubit_logical_z = op_value
                if "logical_x" in op_type:
                    qubit_logical_x = op_value
            continue
        if len(tensor_operators.items()) < 2:
            continue
        temp_z = []
        temp_x = []
        for op_type, op_value in tensor_operators.items():
            if "logical_z" in op_type:
                temp_z = op_value
            if "logical_x" in op_type:
                temp_x = op_value
    rrr = batch_convert_to_binary_vectors(oli)
    L = pauli_to_binary_vector(qubit_logical_x)
    assert L == ""
    lambda_results = minimize_error_operator_weight(L, rrr, mip_focus=3, heuristics=0.5)
    binary_result = apply_mod2_sum(L, rrr, lambda_results)
    assert binary_result == ""
    result = binary_vector_to_pauli(binary_result)
    assert result == ""
    min_wt = calculate_pauli_weight(result)
    assert min_wt == ""
