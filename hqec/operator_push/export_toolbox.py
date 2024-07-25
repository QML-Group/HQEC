import csv


def export_tensor_layer_info_to_csv(tensor_list, filename="tensor_layers.csv"):
    # Open file, ready to write
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # Write title
        writer.writerow(['Tensor ID', 'Layer Number'])

        # Iterate over tensor list
        for tensor in tensor_list:
            writer.writerow([tensor.tensor_id, tensor.layer])

# Example usage:
# export_tensor_layer_info_to_csv(tensor_list, "my_tensor_layers.csv")


def extract_tensor_info(tensor_list):
    tensor_info = {}

    # Iterate through the list of tensors
    for tensor in tensor_list:
        # Extract relevant information from each tensor
        tensor_data = {
            "ups_list": tensor.ups_list,
            "stabilizer_list": tensor.stabilizer_list,
            "layer": tensor.layer
        }
        # Store the extracted information in a dictionary
        tensor_info[tensor.tensor_id] = tensor_data

    return tensor_info

# Example usage:
# Given a tensor_list containing Tensor objects
# tensor_info_dict = extract_tensor_info(tensor_list)
