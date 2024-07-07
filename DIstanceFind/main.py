from DIstanceFind.InputProcessor import process_quantum_csv, collect_stabilizers, collect_logical_xs, collect_logical_zs, \
    read_tensor_layers_from_csv
from DIstanceFind.OperatorProcessor import pauli_to_binary_vector, batch_convert_to_binary_vectors, apply_mod2_sum, \
    binary_vector_to_pauli
from DIstanceFind.DistanceFInder import minimize_logical_operator_weight, calculate_pauli_weight

file_path = "F:\范峻瑜\大学这会儿\【3.0】TU Delft\【2.1】 Y2 Q1\Master Thesis\Distance_VS_n\HTN_vertex_res\L=5\output.csv"
layer_file_path = "F:\范峻瑜\大学这会儿\【3.0】TU Delft\【2.1】 Y2 Q1\Master Thesis\Distance_VS_n\HTN_vertex_res\L=5\\tensor_layers.csv"
tensor_layers = read_tensor_layers_from_csv(layer_file_path)
# print(tensor_layers)
res = process_quantum_csv(file_path)
stabilizers = collect_stabilizers(res)
logical_zs = collect_logical_zs(res)
logical_xs = collect_logical_xs(res)
qubit_logical_z = ''
qubit_logical_x = ''
oli = stabilizers
for tensor_id in tensor_layers:
    tensor_layer = tensor_layers[tensor_id]
    tensor_operators = res[str(tensor_id)]
    if tensor_layer == 0:
        for op_type, op_value in tensor_operators.items():
            if 'logical_z' in op_type:
                qubit_logical_z = op_value
            if 'logical_x' in op_type:
                qubit_logical_x = op_value
        continue
    if len(tensor_operators.items()) < 2:
        continue
    temp_z = []
    temp_x = []
    for op_type, op_value in tensor_operators.items():
        if 'logical_z' in op_type:
            temp_z = op_value
        if 'logical_x' in op_type:
            temp_x = op_value
    '''
        if tensor_layer % 2 == 0 and tensor_layer != 0:
            if 'logical_z' in op_type:
                oli.append(op_value)
        elif tensor_layer % 2 == 1:
            if 'logical_x' in op_type:
                oli.append(op_value)'''
    # bi_temp_z = pauli_to_binary_vector(temp_z)
    # bi_temp_x = pauli_to_binary_vector(temp_x)
    # bi_temp_y = apply_mod2_sum(bi_temp_z, [bi_temp_x], [1])
    # temp_y = binary_vector_to_pauli(bi_temp_y)
    # oli.append(temp_y)
    # oli.append(temp_x)
    # oli.append(temp_z)
# print(oli)
rrr = batch_convert_to_binary_vectors(oli)
L = pauli_to_binary_vector(qubit_logical_x)
# print(L)
lambda_results = minimize_logical_operator_weight(L, rrr, mip_focus=3, heuristics=0.5)
binary_result = apply_mod2_sum(L, rrr, lambda_results)
# print(binary_result)
result = binary_vector_to_pauli(binary_result)
print(result)
min_wt = calculate_pauli_weight(result)
print(f"min_wt: {min_wt}")
