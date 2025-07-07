from QuDec.ErasureDecoder import calculate_recovery_rates_for_p_range
from OperatorPush.Presets.Zero_Rate_HaPPY_new_for_kj import setup_zero_rate_happy
from OperatorPush.PushingToolbox import batch_push, batch_push_multiprocessing
from QuDec.InputProcessor import extract_stabilizers_from_result_dict, extract_logicals_from_result_dict
from QuDec.OutputProcessor import save_results_to_csv

if __name__ == '__main__':
    for R in [0, 1]:
        tensor_list = setup_zero_rate_happy(R=R)
        results_dict = batch_push_multiprocessing(tensor_list)
        stabilizers = extract_stabilizers_from_result_dict(results_dict)
        logical_zs, logical_xs = extract_logicals_from_result_dict(results_dict)
        print(logical_xs)
        logical_operators = [logical_zs[0]] + [logical_xs[0]]
        results = calculate_recovery_rates_for_p_range(n=1000, p_start=0.01, p_end=1.0, p_step=0.1,
                                                       stabilizers=stabilizers, logical_operators=logical_operators,
                                                       n_process=8, cpu_affinity_list=None)
        save_results_to_csv(results, file_path=F'R{R}_rec.csv')
