from QuDec.TN_decoder import tn_quantum_error_correction_decoder_multiprocess
from OperatorPush.Presets.HaPPY import setup_zero_rate_happy
import numpy as np
from QuDec.OutputProcessor import save_results_to_csv

import csv

if __name__ == '__main__':
    task_list = [(1/3, 1/3)]
    for task in task_list:
        rx, rz = task
        for R in [0, 1]:
            tensor_list = setup_zero_rate_happy(R=R)
            p_depo_step = 0.01
            p_depo_start = 0.01
            p_depo_end = 0.55
            if R == 0 or R == 1 or R == 2 or R == 3:
                N = 500
                n_process = 1
            else:
                N = 500
                n_process = 1
            ry = 1 - rx - rz
            print(rx, ry, rz)
            succ_rates = []
            for p_depo in np.arange(p_depo_start, p_depo_end + p_depo_step, p_depo_step):
                print(f"Running at p_depo = {p_depo}")
                succ_rate = tn_quantum_error_correction_decoder_multiprocess(tensor_list=tensor_list, p=p_depo, rx=rx,
                                                                             ry=ry, rz=rz, N=N, n_process=n_process)
                succ_rates.append((p_depo, succ_rate))
            save_results_to_csv(results=succ_rates, file_path=f'R_{R}_rx_{rx}_rz_{rz}.csv')
            print(succ_rates)
