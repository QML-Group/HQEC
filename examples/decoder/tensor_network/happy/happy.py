import os
import tempfile

import numpy as np

from hqec.decoder.decoder_tensor_network import tn_quantum_error_correction_decoder_multiprocess
from hqec.operator_push.presets.zero_rate_happy_new_for_kj import setup_zero_rate_happy
from hqec.output_processor import save_results_to_csv

if __name__ == "__main__":
    task_list = [(1 / 3, 1 / 3)]
    for task in task_list:
        rx, rz = task
        for R in [0, 1]:
            tensor_list = setup_zero_rate_happy(R=R)
            p_depo_step = 0.01
            p_depo_start = 0.01
            p_depo_end = 0.55
            if R == 0 or R == 1 or R == 2 or R == 3:
                N = 500
                n_process = 20
            else:
                N = 200
                n_process = 2
            ry = 1 - rx - rz
            print(rx, ry, rz)
            success_rates = []
            for p_depo in np.arange(p_depo_start, p_depo_end + p_depo_step, p_depo_step):
                print(f"Running at p_depo = {p_depo}")
                success_rate = tn_quantum_error_correction_decoder_multiprocess(
                    tensor_list=tensor_list, p=p_depo, rx=rx, ry=ry, rz=rz, N=N, n_process=n_process
                )
                success_rates.append((p_depo, success_rate))
            save_results_to_csv(
                results=success_rates, file_path=os.path.join(tempfile.gettempdir(), f"R_{R}_rx_{rx}_rz_{rz}.csv")
            )
            print(success_rates)
