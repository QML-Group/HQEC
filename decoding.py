import numpy as np
from QuDec import ErasureDecoder, PauliDecoder, TN_decoder

class Decode:
    def __init__(self, error_rate_start: float, error_rate_end: float, number_spaces: int, stabilizers: list,
            x_logicals: list, z_logicals: list, tensor_list: list, time_limit: float, pauli_mixing_vector: tuple):
        """
        Args:
            error_rate_start: float
            error_rate_end: float
            number_spaces: int
            stabilizers: list
            x_logicals: list
            z_logicals: list
            tensor_list: list
            time_limit: float
            pauli_mixing_vector: tuple where (rx, ry, rz) are relative Pauli proportions
        """
        self.error_rate_range = self.gen_error_rates(error_rate_start=error_rate_start, error_rate_end=error_rate_end, number_spaces=number_spaces)
        self.stabilizers = stabilizers
        self.x_logicals = x_logicals
        self.z_logicals = z_logicals
        self.tensor_list = tensor_list
        self.time_limit = time_limit
        self.pauli_mixing_vector = pauli_mixing_vector

    def gen_error_rates(self, error_rate_start, error_rate_end, number_spaces):
        return np.linspace(error_rate_start, error_rate_end, number_spaces)

    def erasure(self, mc_trials: int):
        logicals = self.z_logicals + self.x_logicals
        recovery_rates = ErasureDecoder.calculate_recovery_rates_for_p_range(n=mc_trials, p_start=self.error_rate_range[0], p_end=self.error_rate_range[-1], p_step=self.error_rate_range[1] - self.error_rate_range[0], stabilizers=self.stabilizers,logical_operators=logicals, n_process=1, cpu_affinity_list=None)
        return recovery_rates

    def integer_optimization(self, mc_trials: int):
        recovery_rates = PauliDecoder.quantum_error_correction_decoder(tensor_list=self.tensor_list, stabilizers=self.stabilizers, logical_xs=self.x_logicals, logical_zs=self.z_logicals, px=self.pauli_mixing_vector[0], py=self.pauli_mixing_vector[1], pz=self.pauli_mixing_vector[2], N=mc_trials, time_limit=None, mip_focus=0, heuristics=0, output_flag=0)

    def tensor_network(self, mc_trials: int):
        recovery_rates = []
        for phys_error_rate in self.error_rate_range:
            success_rate = TN_decoder.tn_quantum_error_correction_decoder_multiprocess(tensor_list=self.tensor_list, p=phys_error_rate, rx=self.pauli_mixing_vector[0], ry=self.pauli_mixing_vector[1], rz=self.pauli_mixing_vector[2], N=mc_trials, stabilizers=self.stabilizers, logical_x=None, logical_z=None, n_process=1, cpu_affinity_list=None, f=None)

            recovery_rates.append(success_rate)
