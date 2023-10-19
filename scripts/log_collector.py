import os
import csv

log_directory = "/home/shaker/Programs/evooracle_singularity/second_run/outputs"
target_file = "/home/shaker/Documents/Thesis/Writing/data/logs.csv"

# Check if the target file exists
if not os.path.exists(target_file):
    # If it doesn't exist, create it with the header
    with open(target_file, 'w', newline='') as csvfile:
        fieldnames = ["final_test_id", "test_id", "project_dir", "class_name", "method_name", "llm_name", "consider_dev_comments", "SEED"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

# Iterate through all folders in the log directory
for folder_name in os.listdir(log_directory):
    folder_path = os.path.join(log_directory, folder_name)

    # Check if it's a directory
    if os.path.isdir(folder_path):
        parameters_file = os.path.join(folder_path, "parameters.tsv")

        # Check if parameters file exists
        if os.path.exists(parameters_file):
            # Read parameters and append to the target file
            with open(parameters_file, 'r') as infile, open(target_file, 'a', newline='') as outfile:
                fieldnames = ["final_test_id", "test_id", "project_dir", "class_name", "method_name", "llm_name", "consider_dev_comments", "SEED"]
                reader = csv.DictReader(infile, delimiter='\t')
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)

                for row in reader:
                    # Calculate final_test_id as the sum of test_id and SEED
                    row["final_test_id"] = row["test_id"] + str(row["SEED"])
                    writer.writerow(row)

print("Script executed successfully.")
