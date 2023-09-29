import os
from colorama import Fore, Style, init
import subprocess

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
runs = ["run_01", "run_02", "run_03"]

models = ["ocra"]
runs = ["run_03"]

filenames = []

# Iterate through each class
for class_name, class_data in classes.items():
    package, class_path = class_data

    # Iterate through each model
    for model in models:
        # Iterate through each run
        for run in runs:
            # Construct the file name pattern
            file_pattern = f"{class_name}_ESTest_{run}_identical_5_{model}"

            test_path = class_path + "/src/test/java"
            # Construct the full path
            full_path = os.path.join(test_path, package.replace(".", os.path.sep))
            
            # print("full_path: " + full_path)
            
            # Iterate through the directory and its subdirectories
            for root, dirs, files in os.walk(full_path):
                # List all ".java" files matching the pattern
                matching_files = [file for file in files if file.endswith("_EOTest.java") and file.startswith(file_pattern)]
                if matching_files:
                    for file in matching_files:
                        # print("FileName: " + os.path.join(root, file))
                        compiled_file = os.path.join(root, file.replace(".java", ".class"))
                        if not os.path.exists(compiled_file):
                            # print(f"The compiled file at {compiled_file} does not exist. Renaming {file} to {file}.failed.")
                            failed_file_path = os.path.join(root, file.replace(".java", ".java.failed"))
                            os.rename(os.path.join(root, file), failed_file_path)
                            # print(f"{file} renamed to {file}.failed.")
                        else:
                            print(f"The compiled file at {compiled_file} exists.")
                            
                            # TODO run mvn and check if successful
                            # Define your commands
                            commands = [
                                
                            ]
                            
                            def run_command(command, working_directory=None):
                                try:
                                    subprocess.run(command, shell=True, check=True, cwd=working_directory)
                                    print(f"Command '{command}' executed successfully.")
                                    return True
                                except subprocess.CalledProcessError as e:
                                    print(f"Error executing command '{command}': {e}")
                                    return False
                            
                            # Running mvn PIT test for class
                            if run_command(commands[0], working_directory=target_path):
                                print("Compile: " + Fore.GREEN + "SUCCESS", Style.RESET_ALL)
                                is_compiled = True
                                
                                # RUNNING
                                if run_command(commands[1], working_directory=target_path):
                                    print("RUN: " + Fore.GREEN + "SUCCESS", Style.RESET_ALL)
                                    is_run = True
                                else:
                                    print("RUN: " + Fore.RED + "FAIL", Style.RESET_ALL)
                            else:
                                print("Compile: " + Fore.RED + "FAIL", Style.RESET_ALL)

