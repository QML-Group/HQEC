import csv


def save_results_to_csv(results, file_path='recovery_rates.csv'):
    """
    Save recovery rate results to a CSV file in the current directory.

    Args:
    results (list of tuples): Each tuple contains a probability value and its corresponding recovery success rate.
    file_path (str): Path to the CSV file where results will be saved. Defaults to 'recovery_rates.csv' in the current directory.

    Returns:
    None: The results are saved to a CSV file.
    """
    with open(file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Probability', 'Recovery Rate'])
        for result in results:
            writer.writerow(result)

# Example usage:
# results = [(0.0, 1.0), (0.1, 0.846), (0.2, 0.559)]
# save_results_to_csv(results)  # File will be saved as 'recovery_rates.csv' in the current directory
