import os
import csv

def process_csv(input_file):
    # Step 1: Read the CSV file
    with open(input_file, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        rows = list(reader)

    for row in rows:
        # Step 2: Check if the file exists in the specified path
        es_test_path = row['es_test_path']
        if os.path.exists(es_test_path) and os.path.getsize(es_test_path) > 0:
            # Step 3: Read the file
            with open(es_test_path, 'r') as test_file:
                content = test_file.read()

            # Step 4: Check if "es_assertion" is a substring
            es_assertion = row['es_assertion']
            if es_assertion in content:
                # Step 5: Append "es_assertion" and a new line before "eo_assertion"
                eo_assertion = row["eo_assertion"]

                new_content = content.replace(es_assertion, f'{es_assertion}\n{eo_assertion}')

                # Create a backup by renaming the original file
                backup_file = f'{es_test_path}.processed'
                os.rename(es_test_path, backup_file)

                # Write the modified content to the original file
                with open(es_test_path, 'w') as modified_file:
                    modified_file.write(new_content)

if __name__ == "__main__":
    input_csv_file = "/home/shaker/Documents/Thesis/Writing/data/es_enhancer_data.csv"
    process_csv(input_csv_file)
