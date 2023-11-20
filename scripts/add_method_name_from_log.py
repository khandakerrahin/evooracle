import csv
import re

old_csv_file = "/home/shaker/Documents/Thesis/Writing/data/logs.csv"
new_csv_file = "/home/shaker/Programs/evooracle_singularity/second_run/second_evoracle_final_results.csv"
output_csv_file = "/home/shaker/Documents/Thesis/Writing/data/thesis_final_evoracle_final_results.csv"

# Read the OLD_CSV and store method_name values in a dictionary
method_name_dict = {}
with open(old_csv_file, 'r') as old_csv:
    reader = csv.DictReader(old_csv)
    for row in reader:
        method_name_dict[row["final_test_id"]] = row["method_name"]

# Read the NEW_CSV, add a new column "method_name" and write to OUTPUT_CSV
with open(new_csv_file, 'r') as new_csv, open(output_csv_file, 'w', newline='') as output_csv:
    reader = csv.DictReader(new_csv)
    fieldnames = reader.fieldnames + ["test_method_name"] + ["run"]
    writer = csv.DictWriter(output_csv, fieldnames=fieldnames)
    writer.writeheader()

    for row in reader:
        final_test_id = row["test_id"]
        # Check if final_test_id is present in method_name_dict
        if final_test_id in method_name_dict:
            # Add method_name to the row
            row["test_method_name"] = method_name_dict[final_test_id]
            # Use a regular expression to extract "run_01"
            match = re.search(r'run_\d+', final_test_id)
            if match:
                extracted_string = match.group()
                row["run"] = extracted_string
            else:
                row["run"] = ""
        else:
            # If not found, you can set a default value or leave it empty
            row["test_method_name"] = ""
            row["run"] = ""
        writer.writerow(row)

print("Script executed successfully.")
