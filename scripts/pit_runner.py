import csv
import os
import re
from colorama import Fore, Style, init
import subprocess
from pit_report_parser import get_linecov_mutcov_teststrength
import sys
# classes format = class:[package, path]
classes = {
    "BaseSettings":["org.bytedeco.javacv", "/home/shaker/Programs/evooracle_singularity/evo_cluster/projects_db/javacv"],
    "CacheHandler":["io.github.bonigarcia.wdm.cache", "/home/shaker/Programs/evooracle_singularity/evo_cluster/projects_db/webdrivermanager"],
    "NodeInstaller":["com.github.eirslett.maven.plugins.frontend.lib", "/home/shaker/Programs/evooracle_singularity/evo_cluster/projects_db/frontend-maven-plugin/frontend-plugin-core"],
    "NPMInstaller":["com.github.eirslett.maven.plugins.frontend.lib", "/home/shaker/Programs/evooracle_singularity/evo_cluster/projects_db/frontend-maven-plugin/frontend-plugin-core"],
    "Parallel":["org.bytedeco.javacv", "/home/shaker/Programs/evooracle_singularity/evo_cluster/projects_db/javacv"],
    "PnpmInstaller":["com.github.eirslett.maven.plugins.frontend.lib", "/home/shaker/Programs/evooracle_singularity/evo_cluster/projects_db/frontend-maven-plugin/frontend-plugin-core"],
    "PropertiesProviderUtils":["org.jsmart.zerocode.core.utils", "/home/shaker/Programs/evooracle_singularity/evo_cluster/projects_db/zerocode/core"],
    "ResolutionCache":["io.github.bonigarcia.wdm.cache", "/home/shaker/Programs/evooracle_singularity/evo_cluster/projects_db/webdrivermanager"],
    "Seekable":["org.bytedeco.javacv", "/home/shaker/Programs/evooracle_singularity/evo_cluster/projects_db/javacv"],
    "SeekableByteArrayOutputStream":["org.bytedeco.javacv", "/home/shaker/Programs/evooracle_singularity/evo_cluster/projects_db/javacv"],
    "ZeroCodeAssertionsProcessor":["org.jsmart.zerocode.core.engine.preprocessor", "/home/shaker/Programs/evooracle_singularity/evo_cluster/projects_db/zerocode/core"],
    "ZerocodeCorrelationshipLogger":["org.jsmart.zerocode.core.logbuilder", "/home/shaker/Programs/evooracle_singularity/evo_cluster/projects_db/zerocode/core"],
}

models = ["ocra", "mpt", "nous", "vicuna", "wizlm"]
runs = ["run_01", "run_02", "run_03", "run_04", "run_05", "run_06", "run_07"]

# models = ["ocra"]
# runs = ["run_03"]

final_result_file = "/home/shaker/Programs/evooracle_singularity/eo_mutation_scores_second_run.csv"
# open file to write results
if not os.path.exists(final_result_file):
    # If it doesn't exist, create the file with a header row
    with open(final_result_file, mode='w', newline='') as csv_file:
        fieldnames = ["class", "test_class", "model", "run", "eo_test_count", "package", "eo_line_coverage_score", "eo_mutation_coverage_score", "eo_test_strength_score", 
                    "eo_line_coverage", "eo_mutation_coverage", "eo_test_strength", "mvn_pit_command", "mvn_pit_status"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

# Iterate through each class
for class_name, class_data in classes.items():
    package, class_path = class_data

    # Iterate through each model
    for model in models:
        # Iterate through each run
        for run in runs:
            target_tests = []

            # Construct the file name pattern
            file_pattern = f"{class_name}_ESTest_{run}_identical_5_{model}"
            # file_pattern_2 = f"{class_name}_ESTest_{run}_identical_5"
            file_pattern_3 = f"{class_name}_ESTest_{run}_identical_5_(\d+)_EOTest"

            test_path = class_path + "/src/test/java"
            # Construct the full path
            full_path = os.path.join(test_path, package.replace(".", os.path.sep))
            
            # print("full_path: " + full_path)
            
            # Iterate through the directory and its subdirectories
            for root, dirs, files in os.walk(full_path):
                # List all ".java" files matching the pattern
                # matching_files = [file for file in files if file.endswith("_EOTest.java") and file.startswith(file_pattern)]
                matching_files = [file for file in files if file.endswith("_EOTest.java") and (file.startswith(file_pattern) or re.match(file_pattern_3, file))]
                
                if matching_files:
                    for file in matching_files:
                        # if(model=='vicuna'):
                        #     print("FileName: " + os.path.join(root, file))
                        compiled_file = os.path.join(root, file.replace(".java", ".class"))
                        if not os.path.exists(compiled_file):
                            # print(f"The compiled file at {compiled_file} does not exist. Renaming {file} to {file}.failed.")
                            failed_file_path = os.path.join(root, file.replace(".java", ".java.failed"))
                            os.rename(os.path.join(root, file), failed_file_path)
                            # print(f"{file} renamed to {file}.failed.")
                        else:
                            # print(f"The compiled file at {compiled_file} exists.")
                            
                            # TODO run mvn and check if successful
                            
                            # PIT Test command
                            # filename = "{class}_ESTest_{run}_identical_5_{model}_{any_random_id}_EOTest"
                            test_class_name = file.replace(".java", "")
                            
                            target_test = f"{package}.{test_class_name}"
                            target_tests.append(target_test)

                            # print("PIT Command: " + individual_mvn_pit_command)

                            def run_command(command, working_directory=None):
                                try:
                                    subprocess.run(command, shell=True, check=True, cwd=working_directory)
                                    print(f"Command '{command}' executed successfully.")
                                    return True
                                except subprocess.CalledProcessError as e:
                                    print(f"Error executing command '{command}': {e}")
                                    return False
                            
                            # Running mvn PIT test for class
                            # if run_command(individual_mvn_pit_command, working_directory=class_path):
                            #     print("PIT Test: " + Fore.GREEN + "SUCCESS", Style.RESET_ALL)
                                
                            # else:
                            #     print("PIT Test: " + Fore.RED + "FAIL", Style.RESET_ALL)
            
            eo_test_count = len(target_tests)
            eo_line_coverage_score = 0
            eo_mutation_coverage_score = 0
            eo_test_strength_score = 0
            eo_line_coverage = 0
            eo_mutation_coverage = 0
            eo_test_strength = 0
            mvn_pit_status = False

            if target_tests:

                # print("\ntarget_tests:\n" + "\n".join(target_tests))
                comma_separated_target_tests = ",".join(target_tests)
                mvn_pit_command = f"mvn test-compile org.pitest:pitest-maven:mutationCoverage -DtargetClasses={package}.{class_name} -DtargetTests={comma_separated_target_tests}"

                  
                # Running mvn PIT test for class
                if run_command(mvn_pit_command, working_directory=class_path):
                    print("PIT Test: " + Fore.GREEN + "SUCCESS", Style.RESET_ALL)
                    mvn_pit_status = True
                    
                    # TODO parse pit report
                    report_path = os.path.join(class_path, "target/pit-reports/index.html") 
                    eo_line_coverage_score, eo_mutation_coverage_score, eo_test_strength_score, eo_line_coverage, eo_mutation_coverage, eo_test_strength  = get_linecov_mutcov_teststrength(report_path)

                else:
                    print("PIT Test: " + Fore.RED + "FAIL", Style.RESET_ALL)
                
            with open(final_result_file, mode='a', newline='') as csv_file:
                fieldnames = ["class", "test_class", "model", "run", "eo_test_count", "package", "eo_line_coverage_score", "eo_mutation_coverage_score", "eo_test_strength_score", 
                    "eo_line_coverage", "eo_mutation_coverage", "eo_test_strength", "mvn_pit_command", "mvn_pit_status"]

                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                
                writer.writerow({
                    "class": class_name,
                    "test_class": test_class_name,
                    "model": model,
                    "run": run,
                    "eo_test_count": eo_test_count,
                    "package": package, 
                    "eo_line_coverage_score": eo_line_coverage_score,
                    "eo_mutation_coverage_score": eo_mutation_coverage_score, 
                    "eo_test_strength_score": eo_test_strength_score,
                    "eo_line_coverage": eo_line_coverage,
                    "eo_mutation_coverage": eo_mutation_coverage, 
                    "eo_test_strength": eo_test_strength,
                    "mvn_pit_command": mvn_pit_command,
                    "mvn_pit_status": mvn_pit_status
                })
                # sys.exit()
    