# LEGO_HQEC

LEGO_HQEC is designed to accelerate research efficiency in holographic quantum error-correcting codes. The software
implements some operations on a holographic tile:

- Quantum-LEGO-based operator push program on a customizable holographic tile. 
- 3 corresponding decoders: the erasure decoder, the integer optimization decoder, and the tensor network decoder.

# Operator push
The Operator push program is responsible for obtaining the stabilizer generators and logical operators of each seed tensor in a given holographic tensor network at the boundary by using the operator push method of quantum LEGO. 

Some common holographic quantum error correction code tensor networks can be directly extracted from presets. For example, pushing the stabilizer generators and logical operators of the seed tensor of the zero rate HaPPY code to the boundary.

```python
from LEGO_HQEC.OperatorPush.PushingToolbox import batch_push
from LEGO_HQEC.OperatorPush.Presets.HaPPY_code import setup_zero_rate_happy

# Set the radius of the HaPPY code
R = 2

# Call the preset function to obtain the tensor network with a radius R, and store all the generated tensors in a list.
tensor_list = setup_zero_rate_happy(R)

# Use the batch_push() function to push the operators. 
pushed_results = batch_push(tensor_list)

# The result is a dictionary containing all the stabilizer generators and logical operators. 
# Additionally, a CSV file containing all the operator results will be generated.
```


# Decoders
The software provides 3 decoders for holographic quantum error correction codes: the erasure decoder, the integer optimization decoder, and the tensor network decoder.
## Erasure decoder
The erasure decoder can analyze the recoverability of logical information in a holographic quantum error correction code under a given quantum erasure error. An example of a Monte Carlo simulation based on the erasure decoder is as follows:

```python
from LEGO_HQEC.QuDec.ErasureDecoder import calculate_recovery_rates_for_p_range
from LEGO_HQEC.OperatorPush.Presets.HaPPY_code import setup_zero_rate_happy
from LEGO_HQEC.OperatorPush.PushingToolbox import batch_push
from LEGO_HQEC.QuDec.InputProcessor import extract_stabilizers_from_result_dict, extract_logicals_from_result_dict
from LEGO_HQEC.QuDec.OutputProcessor import save_results_to_csv

if __name__ == '__main__':
    # Examine the HaPPY code with radii R=0, 1, 2, and 3, respectively.
    for R in [0, 1, 2, 3]:
        # Obtain the tensor network of the Zero rate HaPPY code with the corresponding radius through the preset.
        tensor_list = setup_zero_rate_happy(R=R)

        # Obtain the operators of the corresponding HaPPY code using the operator push function.
        results_dict = batch_push(tensor_list)

        # Extract the stabilizer generators from the result dict using the built-in function and store them in a list.
        stabilizers = extract_stabilizers_from_result_dict(results_dict)

        # Extract the logical operators Z and X from the result dictionary separately and store them each in a list.
        logical_zs, logical_xs = extract_logicals_from_result_dict(results_dict)

        # Here, we do not distinguish between logical Z and X. 
        # Instead, we combine them into a single list that stores the logical operators.
        logical_operators = [logical_zs[0]] + [logical_xs[0]]

        # Starting from an erasure error rate p of 0.01 to 1.0 with a step size of 0.01, 
        # calculate the recoverability rate for each erasure error rate p. 
        # The number of Monte Carlo trials for each p is n = 1,000.
        results = calculate_recovery_rates_for_p_range(n=1000, p_start=0.01, p_end=1.0, p_step=0.01,
                                                       stabilizers=stabilizers, logical_operators=logical_operators)

        # Store the recoverability rate curve data for this radius R zero rate HaPPY code into a CSV file.
        save_results_to_csv(results, file_path=F'R{R}_rec.csv')
```

## Tensor network decoder
The tensor network decoder can analyze the recoverability of logical information in a holographic quantum error correction code under a given Pauli quantum error. It has excellent decoding performance and is highly recommended. An example of a Monte Carlo simulation based on the tensor network decoder is as follows:

```python
from LEGO_HQEC.QuDec.TN_decoder import tn_quantum_error_correction_decoder_multiprocess
from LEGO_HQEC.OperatorPush.Presets.HaPPY_code import setup_zero_rate_happy
import numpy as np
from LEGO_HQEC.QuDec.OutputProcessor import save_results_to_csv

if __name__ == '__main__':
    task_list = [(1 / 3, 1 / 3)]
    for task in task_list:
        rx, rz = task
        for R in [0, 1, 2]:
            tensor_list = setup_zero_rate_happy(R=R)
            p_depo_step = 0.01
            p_depo_start = 0.01
            p_depo_end = 0.55
            N = 1000
            n_process = 16
            ry = 1 - rx - rz
            succ_rates = []
            for p_depo in np.arange(p_depo_start, p_depo_end + p_depo_step, p_depo_step):
                print(f"Running at p_depo = {p_depo}")
                succ_rate = tn_quantum_error_correction_decoder_multiprocess(tensor_list=tensor_list, p=p_depo, rx=rx,
                                                                             ry=ry, rz=rz, N=N, n_process=n_process)
                succ_rates.append((p_depo, succ_rate))
            save_results_to_csv(results=succ_rates, file_path=f'R_{R}_rx_{rx}_rz_{rz}.csv')

```

## Integer optimization decoder
The integer optimization decoder can analyze the recoverability of logical information in a holographic quantum error correction code under a given Pauli quantum error. It is important to note that using the integer optimization decoder requires a Gurobi license.

# Performance
## Operator push
Current implementation is hardcoded to [p, q] = [p, 4] or [p, q] = [4, 5]. The time consumed varies significantly depending on the radius of the holographic code. On a desktop with a 5.7 GHz Intel i9 14900k processor and 64 GB of DDR5 4800MHz RAM, the time taken for operator push using the HaPPY code with different radii in a single-threaded mode is shown in the figure below.
![Operator_Push_Speed.png](readme_pics/Operator_Push_Speed.png)

## Decoders
### Erasure Decoder
The time consumed for one decoding process, under a p = 50% erasure probability, using the zero-rate HaPPY code with R=0,1,2,3,4 as an example, is shown in the figure below.
![Erasure_Decoding_Speed.png](readme_pics/Erasure_Decoding_Speed.png)

### Tensor Network Decoder
Using the zero-rate HaPPY code with R=0,1,2,3,4 as an example, the time consumed for one decoding process under a 15% depolarization error probability, using a tensor network decoder, is shown in the figure below.
![TN_Decoding_Speed.png](readme_pics/TN_Decoding_Speed.png)

### Integer-Optimization Decoder
The performance overhead of the integer optimization decoder increases exponentially as the number of physical qubits increases. In other words, its performance overhead grows double-exponentially with the radius R. Therefore, when a tensor network decoder is available, the use of the integer optimization decoder is not recommended.

This is the first "lite" version of HQEC operator push package. It contains an example of heptagon Steane Code.

## Dependencies

You'll need to have this software installed before carrying on:

- `git`
- `python` >= 3.9
- `pipx`

### Linux

```shell
apt-get update -qq -y
apt-get upgrade -qq -y
apt-get install git python3 pipx
pipx ensurepath
source ~/.bashrc
```
