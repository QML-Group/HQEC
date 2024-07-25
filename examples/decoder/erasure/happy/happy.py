import os
import tempfile

from hqec.decoder.decoder_erasure import calculate_recovery_rates_for_p_range
from hqec.input_processor import extract_stabilizers_from_result_dict, extract_logicals_from_result_dict
from hqec.operator_push.presets.zero_rate_happy_new_for_kj import setup_zero_rate_happy
from hqec.operator_push.push_toolbox import batch_push_multiprocessing
from hqec.output_processor import save_results_to_csv


if __name__ == '__main__':
    for R in [0, 1, 2, 3]:
        tensor_list = setup_zero_rate_happy(R=R)
        results_dict = batch_push_multiprocessing(tensor_list)
        stabilizers = extract_stabilizers_from_result_dict(results_dict)
        logical_zs, logical_xs = extract_logicals_from_result_dict(results_dict)
        print(logical_xs)
        logical_operators = [logical_zs[0]] + [logical_xs[0]]
        results = calculate_recovery_rates_for_p_range(
            n=10000,
            p_start=0.01,
            p_end=1.0,
            p_step=0.01,
            stabilizers=stabilizers,
            logical_operators=logical_operators,
            n_process=24,
            cpu_affinity_list=list(range(8, 32))
        )
        save_results_to_csv(
            results,
            file_path=os.path.join(tempfile.gettempdir(), f'R{R}_rec.csv')
        )
