import csv

# Define default values
partition_name = "identical-5"
incremental_id = 1  # Starting ID

# Open a text file for writing the commands
with open('commands.txt', 'w') as outfile:
    # Open the CSV file for reading
    with open('/home/shaker/evoracle_entries.csv', newline='') as csvfile:
        csvreader = csv.DictReader(csvfile)
        
        # Iterate through each row in the CSV file
        for row in csvreader:
            # Extract values from the CSV row
            id = row['ID']
            project_dir = row['project_dir']
            class_name = row['class_name']
            method_name = row['method_name']
            
            # Define other placeholders
            model = "ggml-stable-vicuna-13B.q4_2.bin"
            dev_comment = "false"
            repetition = "1"
            out_dir = "/storage/SE/evoOracle/evooracle_singularity/outputs"
            
            # Generate the command with placeholders replaced
            command = f"sbatch --output outputs/out_err/run_01_{partition_name}_{id}_eo_out.txt --error outputs/out_err/run_01_{partition_name}_{id}_eo_err.txt -p {partition_name} run_evooracle_singularity.sh run_01_{partition_name}_{id} {project_dir} {class_name} {method_name} {model} {dev_comment} {repetition} {out_dir}"
            
            # Increment the incremental_id
            incremental_id += 1
            
            # Write the generated command to the text file
            outfile.write(command + '\n')
