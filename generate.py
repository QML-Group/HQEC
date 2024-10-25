import numpy as np
from OperatorPush.NetworkToolbox import create_layer_q4, assign_layers_to_tensors
from OperatorPush.TensorToolbox import ensure_minimum_legs, add_logical_legs, get_tensor_from_id, Tensor, has_logical
import itertools
import pandas as pd 

class Generate:

    def __init__(self, tiling:tuple, layers:int, stabilizers:list, logicals:list, which_logical_qubits:list, which_gauge:str):
        """
        Args:

        tiling: reported as a tuple (p,q) for 2-dimensional hyperbolic tilings
        layers: number of layers to inflate out to (int)
        stabilizers: given as a list of strings (list) - ex: ['XXXX', 'ZIZI', 'IZIZ'] for the [[4,1,2]] surface code

        logicals: given as a list of strings (list), wherein the first entry is always the logical X, and the second is always logical Z operator

        which_logical_qubits: given as a list of ints, specifying which tensors possess a logical index (list of int)
        which_gauge: specifies the gauge-fixing constraint for all other 'junk' logical indices in the bulk (either 'i', 'x', 'y', 'z')
        """
        self.tiling = tiling 
        self.layers = layers
        self.stabilizers = stabilizers
        self.logicals = logicals
        self.which_logical_qubits = which_logical_qubits 
        self.which_gauge = which_gauge


    def calculate_stabilizer_group(self):
        '''
        Args: 

        no new arguments. this function simply calculate the 2^(n-k) stabilizers in the Abelian stabilizer group.
        '''

        # parses all the generators to binary symplectic form
        binary_sym_vectors = []
        for stab in self.stabilizers:
            binaryvec = [0] * 2 * len(stab)
            for i in range(len(stab)):
                match stab[i]:
                    case 'I':
                        continue
                    case 'X':
                        binaryvec[i] = 1
                    case 'Y':
                        binaryvec[i] = 1
                        binaryvec[i + len(stab)] = 1
                    case 'Z':
                        binaryvec[i + len(stab)] = 1

            binary_sym_vectors.append(binaryvec)


        # calculates the full stabilizer group
        ranges = [range(2)] * len(self.stabilizers)

        new_vecs = []
        for coeffs in itertools.product(*ranges):
            newrow = sum(c * v for c, v in zip(coeffs, binary_sym_vectors)) % 2
            new_vecs.append(newrow)

        new_vectors = np.array(new_vectors)
        new_vectors = np.unique(new_vectors, axis=0)

        return new_vectors


    def extract_max_rate_operators(self):

        '''
        generation of the network
        '''
        if type(self.layers) is not int:
            raise ValueError("self.layers is not an int")

        elif self.layers < 0:
            raise ValueError("self.layers <= 0 is not allowed")

        tensor_list = []
        layer_list = []

        if self.layers == 0:
            tensor_0 = Tensor(num_legs=0, tensor_id=0)
            tensor_list.append(tensor_0)

        elif self.layers == 1:
            r1 = create_layer_q4(tensor_list=tensor_list, previous_layer_id_list=[0], legs_per_tensor=self.tiling[0])
            layer_list.append(r1)

        else:
            r1 = create_layer_q4(tensor_list=tensor_list, previous_layer_id_list=[0], legs_per_tensor=self.tiling[0])
            layer_list.append(r1)

            for i, R_num in enumerate(range(2, self.layers + 1)):
                temp = create_layer_q4(tensor_list=tensor_list, previous_layer_id_list=layer_list[i], legs_per_tensor=self.tiling[0])
                layer_list.append(temp)

        '''
        initializes the stabilizers, logical operator index permutations needed
        '''
        # Ensure Minimum Legs to 5 for all tensors
        ensure_minimum_legs(tensor_list=tensor_list, target_leg_number= self.tiling[0], start_idx=0, end_idx=len(tensor_list))

        # Add Logical
        add_logical_legs(tensor_list=tensor_list, start_idx=0, end_idx=len(tensor_list))

        # Assign layer
        assign_layers_to_tensors(tensor_list=tensor_list, center_tensor_id=0)


        # calculate the entire stabilizer group 
        group_stab = calculate_stabilizer_group()

        '''
        assigns stabilizers, logical operators appropriately to the network 
        '''
        # for tensor in tensor_list:

            # Rule application
            neighbor_layers = [get_tensor_from_id(tensor_list, tensor_id).layer for tensor_id in tensor.get_connections()]
            current_layer = tensor.layer

            if all(neighbor_layer > current_layer for neighbor_layer in neighbor_layers):
                # Rule 1
                tensor.ups_list = [UPSa1, UPSa2, UPSa3, UPSa4, UPSa5, UPSa6] # self.stabilizers + self.logicals
                tensor.stabilizer_list = [UPSa1, UPSa2, UPSa3, UPSa4] # self.stabilizers
                tensor.logical_z_list = [UPSa6] # self.logicals[1]
                tensor.logical_x_list = [UPSa5] # self.logicals[0]
            elif any(neighbor_layer < current_layer for neighbor_layer in neighbor_layers): # this whole portion - not sure how to subsistute it!
                upper_neighbors = [layer for layer in neighbor_layers if layer < current_layer]
                if len(upper_neighbors) == 1:
                    # Rule 2
                    tensor.ups_list = ulb
                    tensor.stabilizer_list = [ulb[0], ulb[1]] 
                    tensor.logical_z_list = [ulb[5]]
                    tensor.logical_x_list = [ulb[6]]
                elif len(upper_neighbors) == 2:
                    # Rule 3
                    tensor.ups_list = ul
                    tensor.stabilizer_list = []
                    tensor.logical_z_list = [ul[6]]
                    tensor.logical_x_list = [ul[7]]

        # extracts the relevant gauge checks 
        gauge_checks = extract_gauge_checks()

        return tensor_list


        def extract_gauge_checks(self):
            '''
            Args:
            
            tensor_list: list of tensors and their tensor id 

            extract_gauge_checks: extracts gauge-fixed operators (logical operators which we deem as additional stabilizers)
            '''

            # extract directly from the csv file produced by backend
            dataframe = pd.read_csv('output.csv')

            # reads and adds the gauge-fixed 
            for i in self.which_logical_qubits:
                new_stab = dataframe.iloc[i]

                prefix = f'logical_{self.which_gauge}1 = '

                # Find the entry in the row that starts with the dynamic prefix
                logical_entry = None
                for value in row:
                    if isinstance(value, str) and value.startswith(prefix):
                        # Remove the prefix from the entry
                        logical_entry = value.replace(prefix, '')
                        break

            # not sure how to append this to the list of stabilizers coming from the backend!

            # i also need to remove the junk logical operators from the max-rate list of logical operators that is passed to the decoder! 

